# CredCity — Level 1 (fixed scaling, robust image loading, clearer UI)
# -------------------------------------------------------------------
# Run: python credcity.py
# Folder:
#   assets/
#     bank.jpg (or .jpeg/.png)
#     cafe.jpg
#     city.jpg
#     store.jpg
#     tower.jpg
#
# Notes:
# - If an image can't be found/loaded, you'll see "MISSING: <name>" on screen
#   and a clear warning in the console.
# - Window is resizable; logical size is 1280x720 and scales crisply.

import os, random, pygame

pygame.init()

LOGICAL_W, LOGICAL_H = 1280, 720
SCREEN = pygame.display.set_mode((LOGICAL_W, LOGICAL_H),
                                 pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("CredCity — Level 1 (Fixed)")

CLOCK = pygame.time.Clock()
FPS = 60

# ---------- colors ----------
WHITE=(245,245,245); GREY=(150,150,160); BLACK=(10,10,15)
GREEN=(60,210,130); YELLOW=(245,202,85); RED=(225,75,75)
BLUE=(90,150,240); PURPLE=(150,120,220)

# ---------- fonts ----------
def font(sz, bold=False):
    f = pygame.font.SysFont("arialrounded", sz, bold=bold)
    if f is None:
        f = pygame.font.SysFont("arial", sz, bold=bold)
    return f

FONT_S=font(18); FONT_M=font(24); FONT_L=font(36,True)

def draw_text(surf, text, f, color, pos, center=False, max_width=None, shadow=True):
    """Text with optional wrap + soft shadow for readability."""
    def _blit_line(line, xy):
        if shadow:
            img_s=f.render(line, True, (0,0,0))
            r_s=img_s.get_rect()
            if center: r_s.center=(xy[0]+1, xy[1]+1)
            else: r_s.topleft=(xy[0]+1, xy[1]+1)
            surf.blit(img_s, r_s)
        img=f.render(line, True, color)
        r=img.get_rect()
        if center: r.center=xy
        else: r.topleft=xy
        surf.blit(img, r)
        return r.height

    if max_width is None:
        _blit_line(text, pos if not center else pos)
        return

    words=text.split()
    x,y=pos
    line=""
    for w in words:
        test=(line+" "+w).strip()
        if f.size(test)[0] <= max_width:
            line=test
        else:
            y += _blit_line(line, (x,y)) + 4
            line=w
    if line:
        _blit_line(line, (x,y))

def draw_panel(rect, alpha=60, border=2):
    s=pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (0,0,0,alpha), (0,0,rect[2],rect[3]), border_radius=12)
    pygame.draw.rect(s, (255,255,255,120), (0,0,rect[2],rect[3]), border, border_radius=12)
    SCREEN.blit(s, (rect[0], rect[1]))

def button(rect, label):
    mx,my=pygame.mouse.get_pos(); click=pygame.mouse.get_pressed()[0]
    hovered=pygame.Rect(rect).collidepoint((mx,my))
    draw_panel(rect, 70 if hovered else 45, border=2)
    draw_text(SCREEN,label,FONT_M,WHITE,(rect[0]+rect[2]//2,rect[1]+rect[3]//2-10),center=True)
    return hovered and click

def clamp(v,a,b): return max(a,min(b,v))

# ---------- image loading with aspect-correct scaling ----------
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

def scale_cover(surface, width, height):
    """Scale to cover (preserve aspect), then center-crop to width x height."""
    sw, sh = surface.get_size()
    if sw == 0 or sh == 0:
        return pygame.Surface((width, height))
    scale = max(width / sw, height / sh)
    new_w, new_h = int(sw*scale), int(sh*scale)
    surf = pygame.transform.smoothscale(surface, (new_w, new_h))
    # center-crop
    x = (new_w - width)//2
    y = (new_h - height)//2
    return surf.subsurface(pygame.Rect(x, y, width, height)).copy()

def try_load(path):
    try:
        img = pygame.image.load(path)
        # Use convert() AFTER display is set; preserve alpha if present
        img = img.convert_alpha() if img.get_alpha() else img.convert()
        return img
    except Exception as e:
        print(f"[CredCity] Warning: failed to load {path}: {e}")
        return None

def load_bg_any(basename, fallback_color):
    """
    Try basename with .jpg/.jpeg/.png (case-sensitive/case-insensitive).
    Returns (surface, missing_text or None).
    """
    base_no_ext = os.path.splitext(basename)[0]
    candidates = [
        f"{base_no_ext}.jpg", f"{base_no_ext}.jpeg", f"{base_no_ext}.png",
        f"{base_no_ext}.JPG", f"{base_no_ext}.JPEG", f"{base_no_ext}.PNG"
    ]
    for c in candidates:
        p = os.path.join(ASSETS, c)
        if os.path.exists(p):
            img = try_load(p)
            if img:
                return (scale_cover(img, LOGICAL_W, LOGICAL_H), None)
    # fallback with label
    surf = pygame.Surface((LOGICAL_W, LOGICAL_H))
    surf.fill(fallback_color)
    return (surf, f"MISSING: {basename} (.jpg/.jpeg/.png)")

CITY_BG, CITY_MISS   = load_bg_any("city.jpg",  (40, 60, 80))
BANK_BG, BANK_MISS   = load_bg_any("bank.jpg",  (25, 90, 70))
STORE_BG, STORE_MISS = load_bg_any("store.jpg", (90, 60, 40))
CAFE_BG, CAFE_MISS   = load_bg_any("cafe.jpg",  (80, 45, 60))
TOWER_BG, TOWER_MISS = load_bg_any("tower.jpg", (55, 55, 95))

# ---- Glass banner + sprite loader helpers ----

def draw_glass(rect, alpha=80, border=2):
    """Readable glass panel behind text."""
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, alpha), (0, 0, rect[2], rect[3]), border_radius=14)
    pygame.draw.rect(s, (255, 255, 255, 140), (0, 0, rect[2], rect[3]), border, border_radius=14)
    SCREEN.blit(s, (rect[0], rect[1]))

def draw_card(rect, fill=(20, 20, 25), border_rgba=(255, 255, 255, 160)):
    """
    OPAQUE card (no transparency). Good for teaching notes.
    rect = (x, y, w, h)
    """
    x, y, w, h = rect
    s = pygame.Surface((w, h))  # opaque surface
    s.fill(fill)
    pygame.draw.rect(s, fill, (0, 0, w, h), border_radius=14)
    # subtle border
    border = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(border, border_rgba, (0, 0, w, h), 2, border_radius=14)
    SCREEN.blit(s, (x, y))
    SCREEN.blit(border, (x, y))


def load_sprite_any(basename, target_w, target_h):
    """
    Try assets/<basename> with .png/.jpg/.jpeg (both cases). Returns (scaled_surface or None).
    """
    base = os.path.splitext(basename)[0]
    cand = [f"{base}.png", f"{base}.jpg", f"{base}.jpeg",
            f"{base}.PNG", f"{base}.JPG", f"{base}.JPEG"]
    for c in cand:
        p = os.path.join(ASSETS, c)
        if os.path.exists(p):
            img = try_load(p)
            if img:
                # keep aspect; fit inside target box
                sw, sh = img.get_size()
                scale = min(target_w / sw, target_h / sh)
                new = pygame.transform.smoothscale(img, (int(sw*scale), int(sh*scale)))
                return new
    print(f"[CredCity] Optional sprite missing: {basename} (looking for .png/.jpg/.jpeg)")
    return None

# Try to load a cart sprite (optional). Place 'cart.png' in assets/ if you have one.
CART_IMG = load_sprite_any("cart.png", 110, 64)  # will be None if you don't add the file
ELEVATOR_IMG = load_sprite_any("elevator.png", 160, 100) # used in Tower


# ---------- global state ----------
STATE_CITY="city"; STATE_BANK="bank"; STATE_STORE="store"; STATE_CAFE="cafe"; STATE_TOWER="tower"
credit_score=650

player=pygame.Rect(100,600,30,40)
SPEED=5
LOCATIONS={
    "bank":  pygame.Rect(170, 300, 190, 120),
    "store": pygame.Rect(950, 380, 220, 120),
    "cafe":  pygame.Rect(740, 210, 200, 100),
    "tower": pygame.Rect(470, 440, 190, 180),
}
state=STATE_CITY

def draw_hud():
    bar=pygame.Surface((LOGICAL_W,60),pygame.SRCALPHA); bar.fill((0,0,0,140)); SCREEN.blit(bar,(0,0))
    draw_text(SCREEN,"CredCity — Level 1",FONT_L,WHITE,(20,8))
    draw_text(SCREEN,f"Credit Score: {credit_score}",FONT_M,WHITE,(LOGICAL_W-340,12))
    # meter
    mx,my,mw,mh=LOGICAL_W-340,38,320,16
    pygame.draw.rect(SCREEN,(255,255,255,110),(mx,my,mw,mh),2,border_radius=8)
    r=(credit_score-300)/550
    col=GREEN if r>0.6 else YELLOW if r>0.35 else RED
    pygame.draw.rect(SCREEN,col,(mx+2,my+2,int((mw-4)*clamp(r,0,1)),mh-4),border_radius=6)

def add_credit(delta):
    global credit_score
    credit_score = clamp(credit_score + int(delta), 300, 850)

# ============================================================
# BANK — drag paper applications to teller windows
# ============================================================

class Paper:
    def __init__(self, label, pos):
        self.label=label
        self.rect=pygame.Rect(pos[0],pos[1],260,44)
        self.drag=False; self.off=(0,0); self.placed=None
    def handle(self,e):
        if e.type==pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.drag=True; self.off=(self.rect.x-e.pos[0], self.rect.y-e.pos[1])
        elif e.type==pygame.MOUSEBUTTONUP: self.drag=False
        elif e.type==pygame.MOUSEMOTION and self.drag:
            self.rect.topleft=(e.pos[0]+self.off[0], e.pos[1]+self.off[1])
    def draw(self):
        draw_panel((self.rect.x, self.rect.y, self.rect.w, self.rect.h), alpha=70, border=2)
        draw_text(SCREEN,self.label,FONT_M,WHITE,(self.rect.x+10,self.rect.y+10))

class BankScene:
    WINDOWS=[
        ("Teller A: Credit Cards / Lines", "Revolving credit you can reuse; pay monthly."),
        ("Teller B: Installment Loans", "Fixed amount with equal monthly payments."),
        ("Mortgage Desk", "Home loans over long terms, secured by property."),
        ("Student Loans", "Education loans; sometimes allow in-school deferment."),
        ("Info Kiosk", "General questions & new account inquiries.")
    ]
    PAPERS=[
        ("Application: Credit Card",0),
        ("Request: Line of Credit",0),
        ("Application: Car Loan",1),
        ("Application: Mortgage",2),
        ("Request: Student Loan",3),
        ("Question: How to start?",4),
    ]
    def __init__(self): self.reset()
    def reset(self):
        self.targets=[]; self.papers=[]
        right_x=LOGICAL_W//2+40; y=150; sp=92
        for i,(name,desc) in enumerate(self.WINDOWS):
            r=pygame.Rect(right_x, y+i*sp, 520, 70)
            self.targets.append((r,name,desc))
        left_x=80
        labels=list(self.PAPERS); random.shuffle(labels)
        for i,(lab,ans) in enumerate(labels):
            p=Paper(lab,(left_x, 150+i*sp)); p.answer=ans; self.papers.append(p)
        self.finished=False; self.correct=None
    def handle(self,e):
        for p in self.papers: p.handle(e)
        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: set_state(STATE_CITY)
        if e.type==pygame.KEYDOWN and e.key==pygame.K_r: self.reset()
    def update(self):
        if self.finished: return
        mouse_up=pygame.mouse.get_pressed()[0]==0
        if mouse_up:
            for p in self.papers:
                p.placed=None
                for idx,(rect,_,_) in enumerate(self.targets):
                    if p.rect.colliderect(rect):
                        p.rect.topleft=(rect.x+8, rect.y+8); p.placed=idx
        if all(p.placed is not None for p in self.papers):
            good=sum(1 for p in self.papers if p.placed==p.answer)
            self.finished=True; self.correct=good
            add_credit(good*8 - (len(self.papers)-good)*3)
    def draw(self):
        SCREEN.blit(BANK_BG,(0,0))
        if BANK_MISS:
            draw_text(SCREEN, BANK_MISS, FONT_M, WHITE, (20, LOGICAL_H-34))
        draw_hud()
        draw_text(SCREEN,"BANK — Route Applications to the Right Window",FONT_L,WHITE,(40,80))
        draw_text(SCREEN,"Drag each paper to the matching counter/window. (R to reshuffle, ESC to city)",FONT_S,WHITE,(40,120))
        for (rect,name,desc) in self.targets:
            draw_panel((rect.x, rect.y, rect.w, rect.h), alpha=45, border=2)
            draw_text(SCREEN,name,FONT_M,WHITE,(rect.x+12,rect.y+6))
            draw_text(SCREEN,desc,FONT_S,WHITE,(rect.x+12,rect.y+34),max_width=rect.w-24)
        for p in self.papers: p.draw()
        if self.finished:
            msg=f"Placed correctly: {self.correct}/{len(self.papers)}. Credit impact applied. ESC to return."
            draw_text(SCREEN,msg,FONT_M,WHITE,(LOGICAL_W//2,LOGICAL_H-40),center=True)

bank=BankScene()

# ============================================================
# STORE — shelves with items; keep utilization ≤30%
# ============================================================

# ======== REPLACE ONLY THIS CLASS ========

class StoreScene:
    """Shelves & Shopping Cart (auto-sized pills + concept explainer)."""
    MAX_ITEMS_ON_SCREEN = 7
    SPAWN_EVERY = 1.15
    ITEM_H = 36
    H_SPACING = 120                   # min horizontal spacing between items on same shelf
    TOP_BANNER_W = 960
    NEED_TAGS = {"Groceries", "Toiletries", "Notebook"}

    def __init__(self):
        self.reset()

    def reset(self):
        self.limit = 1000
        self.balance = 0
        self.cart = pygame.Rect(LOGICAL_W // 2 - 40, LOGICAL_H - 120, 100, 44)

        # shelves start lower so banners don’t crowd labels
        shelf_y = 320
        self.shelves = [pygame.Rect(140, shelf_y + i * 110, LOGICAL_W - 280, 12) for i in range(3)]

        self.items = []           # each: {"rect", "row", "price", "tag", "fall"}
        self.spawn_cd = 0.0
        self.time = 40.0
        self.finished = False
        self.msg = None
        self.purchased = []
        self.lesson_text = ""

        # UI helpers
        self._label_font = font(20)
        self._label_font_small = font(18)
        self.show_concept_timer = 8.0   # seconds to auto-show explainer on start

    # ---------- spawn helpers ----------
    def _free_slot_on_row(self, row, trial_rect):
        """Ensure there's spacing to neighbors on the same shelf."""
        for it in self.items:
            if it["row"] == row:
                if trial_rect.colliderect(it["rect"].inflate(self.H_SPACING, 0)):
                    return False
        return True

    def _measure_pill_width(self, label):
        """Size pill to text (clamped)."""
        tw, _ = self._label_font.size(label)
        min_w, max_w = 90, 200
        return max(min_w, min(max_w, tw + 20))

    def spawn_item(self):
        tags = [
            ("Groceries", 25), ("Toiletries", 35), ("Notebook", 40), ("T-Shirt", 60),
            ("Headphones", 120), ("Console", 200), ("Decor", 75), ("Snack", 15)
        ]
        tag, price = random.choice(tags)
        label = f"{tag} £{price}"
        row = random.randrange(len(self.shelves))

        # pill width depends on text; clamp within shelf
        w = self._measure_pill_width(label)
        h = self.ITEM_H
        shelf = self.shelves[row]
        sx, ex = shelf.x, shelf.right - w

        # try to find a non-overlapping slot
        for _ in range(14):
            x = random.randint(sx, ex)
            trial = pygame.Rect(x, shelf.y - (h + 6), w, h)
            if self._free_slot_on_row(row, trial):
                self.items.append({"rect": trial, "row": row, "price": price,
                                   "tag": tag, "fall": False, "label": label})
                return
        # if no space, skip this spawn

    # ---------- loop ----------
    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                set_state(STATE_CITY)
            if e.key == pygame.K_h:           # bring back the explainer
                self.show_concept_timer = 8.0

    def update(self):
        if self.finished:
            return

        # concept timer
        if self.show_concept_timer > 0:
            self.show_concept_timer -= 1 / FPS

        # move cart
        keys = pygame.key.get_pressed()
        self.cart.x += (keys[pygame.K_RIGHT] or keys[pygame.K_d]
                        - (keys[pygame.K_LEFT] or keys[pygame.K_a])) * 7
        self.cart.clamp_ip(pygame.Rect(0, 180, LOGICAL_W, LOGICAL_H - 180))

        # spawns
        self.spawn_cd += 1 / FPS
        if self.spawn_cd >= self.SPAWN_EVERY and len(self.items) < self.MAX_ITEMS_ON_SCREEN:
            self.spawn_item()
            self.spawn_cd = 0.0

        # knock: only the nearest item above the cart
        if keys[pygame.K_SPACE]:
            cands = [it for it in self.items
                     if not it["fall"] and self.cart.centerx in range(it["rect"].x - 10, it["rect"].right + 10)]
            if cands:
                target = max(cands, key=lambda it: it["rect"].y)
                target["fall"] = True

        # falling + catch
        for it in self.items:
            if it["fall"]:
                it["rect"].y += 4

        for it in list(self.items):
            if it["fall"] and it["rect"].colliderect(self.cart):
                if self.balance + it["price"] <= self.limit:
                    self.balance += it["price"]
                    self.purchased.append({"tag": it["tag"], "price": it["price"]})
                self.items.remove(it)
            elif it["rect"].y > LOGICAL_H:
                self.items.remove(it)

        # timer
        self.time -= 1 / FPS
        if self.time <= 0 and not self.finished:
            util = self.balance / self.limit
            util_pct = int(util * 100)
            delta = 25 if util <= 0.30 else (-10 if util <= 0.50 else -20)
            add_credit(delta)
            self.finished = True

            upshot = ("Nice control—you stayed at or below 30%."
                      if util <= 0.30 else
                      "Close—aim to keep it at or below 30% next time."
                      if util <= 0.50 else
                      "You relied on credit heavily this round.")

            self.msg = f"Time! Utilization: {util_pct}%. {upshot} (Credit impact applied.)"

            # personalized explanation (plain language, based on play)
            needs = sum(1 for p in self.purchased if p["tag"] in self.NEED_TAGS)
            wants = len(self.purchased) - needs
            largest_item = max(self.purchased, key=lambda p: p["price"]) if self.purchased else {"price": 0, "tag": "—"}
            target_30 = int(self.limit * 0.30)
            gap = self.balance - target_30

            if util <= 0.30:
                explain = (
                    f"You used £{self.balance} out of a £{self.limit} limit, so only {util_pct}% of your available credit "
                    f"was in use. That’s the behavior lenders like: it shows you have room left and aren’t depending on credit. "
                    f"In this round you picked {needs} need{'s' if needs!=1 else ''} and {wants} want{'s' if wants!=1 else ''}. "
                    f"Your largest purchase was £{largest_item['price']} ({largest_item['tag']}). Keeping the balance near "
                    f"£{target_30} or lower and paying in full helps your score stay strong and avoids interest."
                )
            elif util <= 0.50:
                explain = (
                    f"You used £{self.balance} of a £{self.limit} limit ({util_pct}%). That’s not bad, but scores tend to look best "
                    f"when the reported balance sits near £{target_30}. You bought {needs} need{'s' if needs!=1 else ''} and "
                    f"{wants} want{'s' if wants!=1 else ''}; the biggest was £{largest_item['price']} ({largest_item['tag']}). "
                    "If you make an early payment or delay a couple of wants, your next statement could show a much lower balance, "
                    "which usually helps the score."
                )
            else:
                explain = (
                    f"You finished at {util_pct}% by spending £{self.balance} of £{self.limit}. That’s about £{max(0,gap)} over the "
                    f"£{target_30} target many lenders like to see. You picked {needs} need{'s' if needs!=1 else ''} and {wants} want"
                    f"{'s' if wants!=1 else ''}; the largest was £{largest_item['price']} ({largest_item['tag']}). "
                    "Cutting one or two wants or paying early brings the reported balance down and reduces the pressure on your score."
                )

            self.lesson_text = explain

    # ---------- drawing ----------
    def _draw_item_pill(self, it):
        r = it["rect"]
        # glass pill
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 110), (0, 0, r.w, r.h), border_radius=12)
        pygame.draw.rect(s, (255, 255, 255, 190), (0, 0, r.w, r.h), 2, border_radius=12)
        SCREEN.blit(s, r.topleft)

        # choose font size that fits
        label = it["label"]
        txt = self._label_font.render(label, True, WHITE)
        if txt.get_width() > r.w - 10:
            txt = self._label_font_small.render(label, True, WHITE)
        SCREEN.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

    def draw(self):
        SCREEN.blit(STORE_BG, (0, 0))
        if STORE_MISS:
            draw_text(SCREEN, STORE_MISS, FONT_S, WHITE, (20, LOGICAL_H - 28))
        draw_hud()

        # compact centered banners
        x = (LOGICAL_W - self.TOP_BANNER_W) // 2
        draw_glass((x, 72, self.TOP_BANNER_W, 64), alpha=95)
        draw_glass((x, 140, self.TOP_BANNER_W, 48), alpha=85)

        draw_text(SCREEN, "STORE — Shelves & Shopping Cart", FONT_L, WHITE, (x + 20, 80))
        draw_text(SCREEN,
                  "Move cart. SPACE to knock a shelf item down; catch to buy. Keep utilization ≤ 30%.",
                  FONT_S, WHITE, (x + 20, 148), max_width=self.TOP_BANNER_W - 40)

        util = self.balance / self.limit
        hud_line = f"Limit £{self.limit} | Balance £{self.balance} | Util {int(util*100)}% | Time {int(max(0,self.time))}s"
        draw_text(SCREEN, hud_line, FONT_M, WHITE, (40, 204))

        # utilization bar under the HUD line
        mx, my, mw, mh = 40, 232, 420, 14
        pygame.draw.rect(SCREEN, (255, 255, 255, 160), (mx, my, mw, mh), 2, border_radius=8)
        col = GREEN if util <= 0.30 else YELLOW if util <= 0.50 else RED
        pygame.draw.rect(SCREEN, col, (mx + 2, my + 2, int((mw - 4) * clamp(util, 0, 1)), mh - 4), border_radius=6)

        # shelves
        for shelf in self.shelves:
            pygame.draw.rect(SCREEN, (255, 255, 255, 235), shelf)

        # highlight current target with a small arrow
        cands = [it for it in self.items
                 if not it["fall"] and self.cart.centerx in range(it["rect"].x - 10, it["rect"].right + 10)]
        if cands:
            target = max(cands, key=lambda it: it["rect"].y)
            pygame.draw.polygon(SCREEN, (255, 255, 255, 220),
                                [(target["rect"].centerx, target["rect"].y - 12),
                                 (target["rect"].centerx - 8, target["rect"].y - 2),
                                 (target["rect"].centerx + 8, target["rect"].y - 2)])

        # items
        for it in self.items:
            self._draw_item_pill(it)

        # cart sprite (optional), fallback to rectangle
        if CART_IMG:
            desired_h = 54
            scale = desired_h / CART_IMG.get_height()
            cart_img = pygame.transform.smoothscale(CART_IMG,
                                                    (int(CART_IMG.get_width() * scale), desired_h))
            cx = self.cart.centerx - cart_img.get_width() // 2
            cy = self.cart.centery - cart_img.get_height() // 2
            SCREEN.blit(cart_img, (cx, cy))
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), self.cart)
            pygame.draw.rect(SCREEN, PURPLE, self.cart.inflate(-10, -10))

        # concept explainer (short, plain English). Press H to show again.
        # concept explainer (plain English). Press H to show again.
        if self.show_concept_timer > 0 and not self.finished:
            w = self.TOP_BANNER_W
            h = 110
            cx = (LOGICAL_W - w) // 2
            cy = 220  # sits below title/instructions and above the first shelf (now at 320)

            # OPAQUE card (no see-through)
            draw_card((cx, cy, w, h))

            concept = (
                "Credit utilization is the ratio of your total credit card balance to your total credit card limit, expressed as a percentage. For example, if you have a $5,000 total credit limit and a $1,000 balance across your cards, your credit utilization is 20% ($1,000 / $5,000). A low credit utilization ratio, ideally below 30%, is generally viewed positively by lenders and can help boost your credit score."
            )
            draw_text(SCREEN, concept, FONT_S, WHITE, (cx + 18, cy + 14), max_width=w - 36)


        draw_text(SCREEN, "Press H for a quick explanation. ESC returns to City.",
                  FONT_S, WHITE, (LOGICAL_W // 2, LOGICAL_H - 26), center=True)

        # End-of-round: dim + neatly sized lesson card
        if self.finished:
            dim = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 120))
            SCREEN.blit(dim, (0, 0))

            x = (LOGICAL_W - self.TOP_BANNER_W) // 2
            draw_glass((x, LOGICAL_H - 260, self.TOP_BANNER_W, 66), alpha=110)
            draw_text(SCREEN, self.msg, FONT_M, WHITE, (x + 20, LOGICAL_H - 246), max_width=self.TOP_BANNER_W - 40)

            draw_glass((x, LOGICAL_H - 190, self.TOP_BANNER_W, 120), alpha=110)
            draw_text(SCREEN, self.lesson_text, FONT_S, WHITE, (x + 20, LOGICAL_H - 176),
                      max_width=self.TOP_BANNER_W - 40)


store = StoreScene()

# ============================================================
# CAFE — drop coins into moving coffee cups (timing)
# ============================================================

class CafeScene:
    def __init__(self): self.reset()
    def reset(self):
        self.till=pygame.Rect(LOGICAL_W//2-90, LOGICAL_H//2-22, 180, 44)
        self.cups=[]; self.spawn=0; self.total=15; self.ontime=0; self.late=0; self.finished=False; self.note=None
        self.coin=None
    def spawn_cup(self):
        x=-70; speed=random.uniform(2.5,4.0)
        self.cups.append({"x":x,"speed":speed})
    def handle(self,e):
        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: set_state(STATE_CITY)
        if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE and not self.finished:
            if self.coin is None:
                self.coin=[self.till.centerx, self.till.y]
    def update(self):
        if self.finished: return
        self.spawn += 1/FPS
        if self.spawn>=0.9 and (len(self.cups)+self.ontime+self.late)<self.total:
            self.spawn=0; self.spawn_cup()
        for c in list(self.cups):
            c["x"]+=c["speed"]
            if c["x"]>LOGICAL_W+60:
                self.cups.remove(c); self.late+=1
        if self.coin:
            self.coin[1]+=6
            if self.coin[1]>=self.till.bottom:
                paid=False
                for c in list(self.cups):
                    rect=pygame.Rect(int(c["x"]), self.till.y, 60, self.till.h)
                    if rect.collidepoint(self.coin[0], self.till.bottom-5):
                        self.ontime+=1; self.cups.remove(c); paid=True; break
                if not paid: self.late+=1
                self.coin=None
        if (self.ontime+self.late)>=self.total and not self.cups:
            rate=self.ontime/self.total
            add_credit(30 if rate>=0.9 else (10 if rate>=0.7 else -15))
            self.finished=True
            self.note="Excellent payment history!" if rate>=0.9 else ("Good—aim for 100% on-time." if rate>=0.7 else "Late payments hurt. Set reminders/auto-pay.")
    def draw(self):
        SCREEN.blit(CAFE_BG,(0,0))
        if CAFE_MISS: draw_text(SCREEN, CAFE_MISS, FONT_M, WHITE, (20, LOGICAL_H-34))
        draw_hud()
        draw_text(SCREEN,"CAFE — Pay the Bill at the Till",FONT_L,WHITE,(40,80))
        draw_text(SCREEN,"Press SPACE to drop a coin into a passing coffee cup at the till (green area). On-time = inside the cup.",FONT_S,WHITE,(40,120),max_width=1200)
        lane=pygame.Rect(60,self.till.y,LOGICAL_W-120,self.till.h)
        pygame.draw.rect(SCREEN,(255,255,255,80),lane,border_radius=12)
        pygame.draw.rect(SCREEN,(70,200,130,200),self.till,border_radius=12)
        pygame.draw.rect(SCREEN,(255,255,255,160),self.till,2,border_radius=12)
        draw_text(SCREEN,"TILL",FONT_M,WHITE,(self.till.centerx,self.till.centery-10),center=True)
        for c in self.cups:
            r=pygame.Rect(int(c["x"]), self.till.y, 60, self.till.h)
            draw_panel((r.x, r.y, r.w, r.h), alpha=65, border=2)
            draw_text(SCREEN,"☕",FONT_M,WHITE,(r.centerx-6,r.y+6))
        if self.coin:
            pygame.draw.circle(SCREEN,YELLOW,(int(self.coin[0]),int(self.coin[1])),10)
            pygame.draw.circle(SCREEN,(255,255,255),(int(self.coin[0]),int(self.coin[1])),2)
        draw_text(SCREEN,f"On-time {self.ontime} | Late {self.late} | Total {self.total}",FONT_M,WHITE,(40,170))
        draw_text(SCREEN,"SPACE = drop coin. ESC = back to City.",FONT_S,WHITE,(LOGICAL_W//2,LOGICAL_H-26),center=True)
        if self.finished and self.note:
            draw_text(SCREEN,self.note+" (Credit impact applied.)",FONT_M,WHITE,(LOGICAL_W//2,LOGICAL_H-54),center=True)

cafe=CafeScene()

# ============================================================
# TOWER — elevator quiz
# ============================================================

# =========================
# CREDIT TOWER — Animated Elevator Quiz (Version 1)
# Drop-in replacement for your TowerScene class
# =========================
# =========================
# CREDIT TOWER — Polished Elevator Quiz (animated + intro + personalized summary)
# =========================
class TowerScene:
    """Ride an elevator by answering credit questions. Intro explainer, smooth rise, shake on wrong."""

    QUESTIONS = [
        # tag = category used for personalized feedback later
        {
            "tag": "payment_history",
            "q": "Your credit score mostly reflects which behaviour?",
            "options": ["Where you shop", "Education", "Income", "On-time payments"],
            "correct": 3,
            "explain": "Payment history is the largest factor. Paying every bill on time shows reliability."
        },
        {
            "tag": "utilization",
            "q": "Why do lenders like utilization around 30% or less?",
            "options": ["It shows control over credit", "It raises your income", "It increases card rewards", "It lowers interest by itself"],
            "correct": 0,
            "explain": "Low utilization means you’re not leaning heavily on credit right now."
        },
        {
            "tag": "inquiries",
            "q": "Opening many new credit accounts quickly can…",
            "options": ["Lower your score temporarily", "Have no effect", "Boost your score quickly", "Raise your salary"],
            "correct": 0,
            "explain": "Multiple applications = more hard inquiries and slightly higher risk for lenders."
        },
        {
            "tag": "age",
            "q": "Why does the length of your credit history help your score?",
            "options": ["It shows long-term reliability", "It proves your age", "It raises limits automatically", "It closes old cards"],
            "correct": 0,
            "explain": "A longer track record lets lenders see steady, responsible habits."
        },
        {
            "tag": "soft_checks",
            "q": "Checking your own credit in an app or website…",
            "options": ["Doesn’t affect your score", "Lowers your score", "Freezes your account", "Raises your score"],
            "correct": 0,
            "explain": "That’s a soft check. Only lender applications are hard checks that can nudge scores."
        },
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        # quiz state
        self.idx = 0
        self.correct_count = 0
        self.selected = None
        self.feedback = ""
        self.explain_timer = 0.0
        self.finished = False
        self.missed_tags = []  # track topics the player struggled with

        # intro explainer card (opaque), toggled with H
        self.show_intro_timer = 6.0  # seconds

        # shaft layout (space for elevator + four guideline floors)
        self.shaft = pygame.Rect(LOGICAL_W - 560, 160, 240, 460)
        top = self.shaft.y + 40
        bottom = self.shaft.bottom - 40
        step = (bottom - top) // 3
        self.floors = [top + i * step for i in range(3, -1, -1)]  # 4 y positions (top..bottom)
        self.floor_idx = 3  # start at bottom
        self.car_y = float(self.floors[self.floor_idx])
        self.target_y = None
        self.moving = False

        # animation
        self.shake_frames = 0
        self.shake_amp = 6
        self.advance_delay = 0.0

        # option rects rebuilt each frame
        self.option_rects = []

    # ---------- input ----------
    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                set_state(STATE_CITY)
            elif e.key == pygame.K_h and not self.finished:
                self.show_intro_timer = 6.0
            elif self.finished and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                set_state(STATE_CITY)

        if e.type == pygame.MOUSEBUTTONDOWN and not self.finished:
            if self.moving or self.shake_frames > 0 or self.advance_delay > 0:
                return
            mx, my = pygame.mouse.get_pos()
            for i, r in enumerate(self.option_rects):
                if r.collidepoint(mx, my):
                    self.selected = i
                    self.evaluate(i)
                    break

    # ---------- logic ----------
    def evaluate(self, choice):
        q = self.QUESTIONS[self.idx]
        if choice == q["correct"]:
            self.feedback = "✅ Correct — going up!"
            self.correct_count += 1
            if self.floor_idx > 0:
                self.floor_idx -= 1
                self.target_y = float(self.floors[self.floor_idx])
                self.moving = True
            self.explain_timer = 1.6
            add_credit(+5)  # small per-question nudge
        else:
            self.feedback = "❌ Not quite."
            self.shake_frames = 24
            self.explain_timer = 3.0
            if q["tag"] not in self.missed_tags:
                self.missed_tags.append(q["tag"])
            add_credit(-3)

        self.advance_delay = 1.0 if choice == q["correct"] else 1.4

    def update(self):
        if self.finished:
            return

        # timers
        if self.show_intro_timer > 0:
            self.show_intro_timer -= 1 / FPS

        if self.explain_timer > 0:
            self.explain_timer -= 1 / FPS

        if self.advance_delay > 0:
            self.advance_delay -= 1 / FPS
            if self.advance_delay <= 0:
                self.next_question()

        # elevator motion (ease)
        if self.moving and self.target_y is not None:
            dy = self.target_y - self.car_y
            if abs(dy) < 0.8:
                self.car_y = self.target_y
                self.target_y = None
                self.moving = False
            else:
                self.car_y += dy * 0.18

        # shake decay
        if self.shake_frames > 0:
            self.shake_frames -= 1

    def next_question(self):
        self.selected = None
        self.feedback = ""
        self.explain_timer = 0.0
        self.idx += 1
        if self.idx >= len(self.QUESTIONS):
            self.end_quiz()

    def end_quiz(self):
        self.finished = True
        rate = self.correct_count / len(self.QUESTIONS)
        # final impact
        if rate >= 0.9:
            add_credit(+25)
            level = "excellent"
        elif rate >= 0.6:
            add_credit(+10)
            level = "solid"
        else:
            add_credit(-10)
            level = "early-stage"

        # personalized, helpful summary (no bullets)
        focus_map = {
            "payment_history": "paying every bill on time",
            "utilization": "keeping balances to about 30% of your limit or less",
            "inquiries": "avoiding lots of new applications at once",
            "age": "letting your good accounts stay open and age",
            "soft_checks": "checking your score freely — it won’t hurt",
        }
        if self.missed_tags:
            topics = ", ".join(focus_map[t] for t in self.missed_tags)
            pointer = f"To climb faster, focus on {topics}. "
        else:
            pointer = ("You hit every major principle. Keep doing what works — "
                       "pay on time, let accounts age, and keep balances modest. ")

        if level == "excellent":
            tone = ("You answered almost everything right. That’s the mindset that builds strong credit in real life: "
                    "steady on-time payments, low balances when statements cut, and few hard checks.")
        elif level == "solid":
            tone = ("You understand the fundamentals. Tighten up one or two areas and your score power will show up quickly. ")
        else:
            tone = ("You’re getting the hang of it. Focus on the biggest levers first and you’ll see progress month by month. ")

        self.summary_text = (
            f"You got {self.correct_count} out of {len(self.QUESTIONS)} — a {level} result. "
            "The elevator rise mirrors how a score grows: it responds to the habits it sees, every month. "
            f"{pointer}{tone}"
            "A practical next step is to pick a bill you can automate and set a reminder a few days before it’s due; "
            "then aim to have your reported balance near thirty percent of your limit when the statement closes."
        )

    # ---------- drawing ----------
        # ---------- drawing ----------
    def draw(self):
        SCREEN.blit(TOWER_BG, (0, 0))
        draw_hud()

        # Title
        draw_text(SCREEN, "CREDIT TOWER — Elevator Quiz", FONT_L, WHITE, (40, 70))
        if self.finished:
            self.draw_summary()
            return

        # Current question
        q = self.QUESTIONS[self.idx]
        draw_text(SCREEN, q["q"], FONT_M, WHITE, (40, 140), max_width=980)

        # Shaft and floors
        pygame.draw.rect(SCREEN, (255, 255, 255, 80), self.shaft, 2, border_radius=14)
        for fy in self.floors:
            pygame.draw.line(SCREEN, (255, 255, 255, 130),
                             (self.shaft.x + 14, fy), (self.shaft.right - 14, fy), 1)

        # Elevator car (shake on wrong)
        shake_x = 0
        if self.shake_frames > 0:
            shake_x = self.shake_amp if (self.shake_frames // 2) % 2 == 0 else -self.shake_amp

        car_rect = pygame.Rect(self.shaft.x + 32 + shake_x, int(self.car_y - 44),
                               self.shaft.w - 64, 88)

        if ELEVATOR_IMG:
            img = pygame.transform.smoothscale(ELEVATOR_IMG, (car_rect.w, car_rect.h))
            SCREEN.blit(img, (car_rect.x, car_rect.y))
        else:
            draw_glass((car_rect.x, car_rect.y, car_rect.w, car_rect.h), alpha=70, border=2)
            draw_text(SCREEN, "Elevator", FONT_S, WHITE,
                      (car_rect.centerx, car_rect.centery - 8), center=True)

        # Answer options on the right — auto-size to text (no overflow), right-aligned
        self.option_rects = []
        right_margin = 40
        base_y = 210
        gap_y = 86
        MIN_W, MAX_W = 220, 420
        PAD_X, PAD_Y = 18, 14

        for i, opt in enumerate(q["options"]):
            tw, th = FONT_M.size(opt)
            w = int(clamp(tw + PAD_X * 2, MIN_W, MAX_W))
            h = max(58, th + PAD_Y * 2)

            x = LOGICAL_W - right_margin - w  # right-aligned to the screen edge
            y = base_y + i * gap_y
            r = pygame.Rect(x, y, w, h)

            alpha = 120 if self.selected is None else (190 if i == self.selected else 60)
            draw_glass((r.x, r.y, r.w, r.h), alpha=alpha, border=2)
            draw_text(SCREEN, opt, FONT_M, WHITE, (r.centerx, r.centery - 10),
                      center=True, max_width=r.w - PAD_X * 2)
            self.option_rects.append(r)

        # Feedback + short explanation (opaque card)
        if self.feedback:
            draw_text(SCREEN, self.feedback, FONT_M, WHITE, (40, 600))
            if self.explain_timer > 0:
                exp_w, exp_h = 1000, 110
                exp_x, exp_y = 40, 620 - exp_h
                draw_card((exp_x, exp_y, exp_w, exp_h))
                draw_text(SCREEN, q["explain"], FONT_S, WHITE,
                          (exp_x + 16, exp_y + 14), max_width=exp_w - 32)

        # INTRO EXPLAINER — draw LAST so it’s always on top
        if self.show_intro_timer > 0:
            w, h = 1060, 110
            x = (LOGICAL_W - w) // 2
            y = 180
            draw_card((x, y, w, h))
            intro = (
                "What is this quiz testing? It checks whether you know which everyday habits move a credit score. "
                "Scores mainly respond to paying on time and keeping balances low compared to your limits. "
                "They don’t care about income or education directly, and checking your own score doesn’t hurt it."
            )
            draw_text(SCREEN, intro, FONT_S, WHITE, (x + 16, y + 14), max_width=w - 32)

        # Footer
        draw_text(SCREEN,
                  "Click a floor panel to move the elevator. Press H for a quick explainer. ESC to City.",
                  FONT_S, WHITE, (LOGICAL_W // 2, LOGICAL_H - 26), center=True)


    def draw_summary(self):
        # Dim background
        dim = pygame.Surface((LOGICAL_W, LOGICAL_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        SCREEN.blit(dim, (0, 0))

        # Prepare text
        title = f"Quiz complete — {self.correct_count}/{len(self.QUESTIONS)} correct"
        body = self.summary_text

        # Wrap body text and compute box height dynamically
        lines = []
        words = body.split(" ")
        line = ""
        for word in words:
            test = line + word + " "
            if FONT_M.size(test)[0] > 1040:  # width limit
                lines.append(line)
                line = word + " "
            else:
                line = test
        if line:
            lines.append(line)

        # Calculate box height
        line_height = FONT_M.get_linesize()
        text_height = len(lines) * line_height
        padding_top = 80
        padding_bottom = 40
        h = padding_top + text_height + padding_bottom

        # Keep it within reasonable bounds
        h = max(260, min(h, LOGICAL_H - 160))
        w = 1080
        x = (LOGICAL_W - w) // 2
        y = (LOGICAL_H - h) // 2

        # Draw box
        draw_card((x, y, w, h))
        draw_text(SCREEN, title, FONT_L, WHITE, (x + 20, y + 18))
        draw_text(SCREEN, body, FONT_M, WHITE, (x + 20, y + 86), max_width=w - 40)

        # Footer
        draw_text(SCREEN, "Press ENTER (or SPACE) to return to the City.",
                  FONT_S, WHITE, (LOGICAL_W // 2, LOGICAL_H - 36), center=True)



tower=TowerScene()

# ============================================================
# CITY
# ============================================================

def set_state(s):
    global state
    state=s
    if s==STATE_BANK:  bank.reset()
    if s==STATE_STORE: store.reset()
    if s==STATE_CAFE:  cafe.reset()
    if s==STATE_TOWER: tower.reset()

def draw_hub_miss_labels():
    # show missing labels once in city to help debug asset filenames
    labels=[]
    if CITY_MISS:  labels.append(CITY_MISS)
    if BANK_MISS:  labels.append(BANK_MISS)
    if STORE_MISS: labels.append(STORE_MISS)
    if CAFE_MISS:  labels.append(CAFE_MISS)
    if TOWER_MISS: labels.append(TOWER_MISS)
    y=LOGICAL_H-24*len(labels)-10
    for m in labels:
        draw_text(SCREEN, m, FONT_S, WHITE, (10, y)); y+=24

def city_update():
    keys=pygame.key.get_pressed()
    player.x += (keys[pygame.K_RIGHT] or keys[pygame.K_d] - (keys[pygame.K_LEFT] or keys[pygame.K_a]))*SPEED
    player.y += (keys[pygame.K_DOWN]  or keys[pygame.K_s] - (keys[pygame.K_UP]   or keys[pygame.K_w]))*SPEED
    player.clamp_ip(pygame.Rect(0,60,LOGICAL_W,LOGICAL_H-60))

def city_draw():
    SCREEN.blit(CITY_BG,(0,0))
    draw_hud()
    for name,rect in LOCATIONS.items():
        draw_panel((rect.x, rect.y, rect.w, rect.h), alpha=45, border=2)
        title={"bank":"Bank","store":"Store","cafe":"Cafe","tower":"Credit Tower"}[name]
        draw_text(SCREEN,title,FONT_M,WHITE,(rect.centerx,rect.y-22),center=True)
    pygame.draw.rect(SCREEN,(255,255,255),player)
    pygame.draw.rect(SCREEN,BLUE,player.inflate(-8,-8))
    mouse=pygame.mouse.get_pos()
    for name,rect in LOCATIONS.items():
        if player.colliderect(rect.inflate(30,30)) or rect.collidepoint(mouse):
            tip={
                "bank":"Route applications to teller windows",
                "store":"Grab shelf items; keep utilization ≤30%",
                "cafe":"Drop coins into cups at the till",
                "tower":"Elevator quiz & wrap-up"
            }[name]
            draw_text(SCREEN,tip,FONT_M,WHITE,(rect.centerx,rect.bottom+8),center=True)
            if button((rect.centerx-70, rect.centery-18, 140, 36),"Enter"):
                set_state(name)
    draw_text(SCREEN,"Move with WASD/Arrows. Click a building to enter.",
              FONT_M,WHITE,(LOGICAL_W//2,LOGICAL_H-26),center=True)
    draw_hub_miss_labels()

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    global state
    running=True
    while running:
        CLOCK.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if state==STATE_CITY:
                if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: running=False
            elif state==STATE_BANK:  bank.handle(e)
            elif state==STATE_STORE: store.handle(e)
            elif state==STATE_CAFE:  cafe.handle(e)
            elif state==STATE_TOWER: tower.handle(e)

        if state==STATE_CITY: city_update()
        elif state==STATE_BANK:  bank.update()
        elif state==STATE_STORE: store.update()
        elif state==STATE_CAFE:  cafe.update()
        elif state==STATE_TOWER: tower.update()

        if state==STATE_CITY: city_draw()
        elif state==STATE_BANK:  bank.draw()
        elif state==STATE_STORE: store.draw()
        elif state==STATE_CAFE:  cafe.draw()
        elif state==STATE_TOWER: tower.draw()

        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()

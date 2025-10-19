from langchain_aws import BedrockLLM

llm = BedrockLLM(
    credentials_profile_name="bedrock-admin", model_id="amazon.titan-text-express-v1"
)
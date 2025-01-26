# LLM 기본 파이프라인 선언 
from langchain.llms import OpenAI
from langchain.pipelines import TextPipeline

# Step 1: Install LangChain
# You can install LangChain via pip if you haven't already
# pip install langchain

# Step 2: Define a function to read content from a .txt file
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Step 3: Create a text-generation pipeline using LangChain
class TextGeneratePipeline(TextPipeline):
    def __init__(self, model_name='gpt-3.5-turbo'):
        self.llm = OpenAI(model_name=model_name)
    
    def generate_text(self, input_text):
        response = self.llm(input_text)
        return response['choices'][0]['text']

# Example usage
if __name__ == "__main__":
    # Define your .txt file path
    file_path = 'path/to/your/textfile.txt'

    # Read the content from the .txt file
    input_text = read_txt_file(file_path)

    # Initialize the text-generation pipeline
    pipeline = TextGeneratePipeline()

    # Generate text based on the input text
    generated_text = pipeline.generate_text(input_text)

    # Print the generated text
    print("Generated Text:")
    print(generated_text)

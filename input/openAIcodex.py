import openai
from openai import OpenAI
openai.api_key = "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"

client = OpenAI(api_key="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")

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message)

import os
import openai

openai.api_key = "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"

response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Convert this text to a programmatic command:\n\nExample: Ask Constance if we need some bread\nOutput: send-msg `find constance` Do we need some bread?\n\nReach out to the ski store and figure out if I can get my skis fixed before I leave on Thursday",
    temperature=0,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["\n"])

print(response)

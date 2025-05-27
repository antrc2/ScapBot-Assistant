# API Document

1. Khi muốn chat:
    ```
    {
        "messages": [
            {
                "role": "system",
                "content": "Bạn là một trợ lí ảo của ScapBot"
            },
            {
                "role": "user",
                "content": <câu hỏi>
            }
        ]
    }
    ```
2. Khi muốn chat liên tiếp:
    ```
    {
        "messages": [
            {
                "role": "system",
                "content": "Bạn là một trợ lí ảo của ScapBot"
            },
            {
                "role": "user",
                "content": "<câu hỏi 1>"
            },
            {
                "role": "assistant",
                "content": "<câu trả lời 1>"
            },
            {
                "role": "user",
                "content": "<câu hỏi 2>"
            }
        ]
    }
    ```
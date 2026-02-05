from llm_helper import llm
from few_shot import Fewshotposts

few_shot = Fewshotposts()


def get_length_str(length: str) -> str:
    """Convert length category to human-readable line count."""
    length = length.lower()
    if length == "short":
        return "1 to 5 lines"
    if length == "medium":
        return "6 to 10 lines"
    if length == "long":
        return "11 to 15 lines"
    return "Unknown length"


def generate_post(length: str, language: str, tag: str) -> str:
    """
    Generate a LinkedIn post using few-shot examples.

    Args:
        length: "short", "medium", or "long"
        language: "english", "hinglish", "hindi"
        tag: topic/tag for the post

    Returns:
        Generated post as a string
    """
    # Normalize inputs for filtering
    length_norm = length.lower()
    language_norm = language.lower()
    tag_norm = tag.lower()

    # Build prompt
    prompt = get_prompt(length_norm, language_norm, tag_norm)

    # Send to LLM
    response = llm.invoke(prompt)
    return response.content


def get_prompt(length: str, language: str, tag: str) -> str:
    """
    Construct the few-shot prompt for the LLM.

    Args:
        length: normalized lowercase length
        language: normalized lowercase language
        tag: normalized lowercase tag

    Returns:
        Full prompt string
    """

    # Display-friendly versions
    length_str = get_length_str(length)
    language_display = language.capitalize()
    tag_display = " ".join(word.capitalize() for word in tag.split())

    # Base instructions
    prompt = f'''
Generate a LinkedIn post using the following information. No preamble.

1) Topic: {tag_display}
2) Length: {length_str}
3) Language: {language_display}
If Language is Hinglish, it means it is a mix of Hindi and English. 
The script for the generated post should always be English.
'''

    # Fetch few-shot examples
    examples = few_shot.get_filtered_posts(length, language, tag)

    if examples:
        prompt += "\n4) Use the writing style as per the following examples:"

        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f'\n\nExample {i+1}:\n{post_text}'

            if i == 1:  # Max 2 examples
                break
    else:
        prompt += "\n(No few-shot examples available for this combination.)"

    return prompt


if __name__ == "__main__":
    post = generate_post("Medium", "English", "Mental Health")
    print(post)

import json
from llm_helper import llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
import re


def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'[\ud800-\udfff]', '', text)
    return text

def deep_clean(obj):
    if isinstance(obj, dict):
        return {k: deep_clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean(v) for v in obj]
    elif isinstance(obj, str):
        return re.sub(r'[\ud800-\udfff]', '', obj)
    else:
        return obj

def process_posts(raw_file_path, processed_file_path):
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)

    enriched_posts = []
    for post in posts:
        clean_post_text = clean_text(post['text'])
        metadata = extract_metadata(clean_post_text)
        post_with_metadata = post | metadata
        enriched_posts.append(post_with_metadata)

    # ✅ UNIFY TAGS AFTER METADATA EXTRACTION
    unified_tags = get_unified_tags(enriched_posts)

    for post in enriched_posts:
       normalized_tags = []
       for tag in post["tags"]:
         tag_key = tag.strip()

         if tag_key in unified_tags:
            normalized_tags.append(unified_tags[tag_key])
         else:
            # ✅ fallback if LLM didn't map it
            normalized_tags.append(tag_key)

    # ✅ remove duplicates
       post["tags"] = list(set(normalized_tags))


    # ✅ WRITE FINAL CLEAN OUTPUT
    # ✅ FULL DATA SANITIZATION BEFORE SAVING
    enriched_posts = deep_clean(enriched_posts)

    with open(processed_file_path, "w", encoding="utf-8", errors="ignore") as outfile:
      json.dump(enriched_posts, outfile, ensure_ascii=False, indent=4)



    return enriched_posts  # ✅ SAFE RETURN


def extract_metadata(post):
    template = '''
You are given a LinkedIn post. You need to extract number of lines, language of the post and tags.
1. Return a valid JSON. No preamble.
2. JSON object should have exactly three keys: line_count, language and tags.
3. tags is an array of text tags. Extract maximum two tags.
4. Language should be English or Hinglish (Hinglish means Hindi + English)

Here is the actual post on which you need to perform this task:  
{post}
'''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)

        for key, value in res.items():
            res[key] = clean_text(value)

    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")

    return res


def get_unified_tags(posts_with_metadata):
    unique_tags = set()

    for post in posts_with_metadata:
        unique_tags.update(post['tags'])

    unique_tags_list = ','.join(unique_tags)

    template = '''I will give you a list of tags. You need to unify tags with the following requirements,
    1. Tags are unified and merged to create a shorter list. 
    2. Each tag should follow title case convention
    3. Output should be a JSON object. No preamble.
    4. Output should have mapping of original tag and the unified tag. 
    
    Here is the list of tags: 
    {tags}
    '''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"tags": str(unique_tags_list)})

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(response.content)
    except OutputParserException:
        raise OutputParserException("Context too big. Unable to parse jobs.")

    return res


# ✅ ✅ ✅ ONLY ENTRY POINT
if __name__ == "__main__":
    enriched_posts = process_posts(
        "raw_post.json",
        "processed_posts.json"
    )

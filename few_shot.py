import pandas as pd
import json

class Fewshotposts:
    def __init__(self,filepath="/Users/varshashibu/Documents/linkedin Post Generator/data/processed_posts.json"):
        self.df=None
        self.unique_tags=None
        self.load_posts(filepath)

    def load_posts(self,filepath):
        with open(filepath,encoding="utf-8") as f:
            posts=json.load(f)
            self.df=pd.json_normalize(posts)
            self.df['length']=self.df['line_count'].apply(self.categorize_length)
            all_tags=self.df['tags'].apply(lambda x:x).sum()
            self.unique_tags=list(set(all_tags))
    
    def get_filtered_posts(self, length, language, tag):

        # Normalize input
        language = language.strip().lower()
        tag = tag.strip().lower()
        length = length.strip().lower()

        # Normalize df
        self.df['language'] = self.df['language'].str.lower()
        self.df['tags'] = self.df['tags'].apply(lambda x: [t.lower() for t in x])
        self.df['length'] = self.df['length'].str.lower()

        # Custom language mapping
        if language == "hinglish":
            valid_langs = ["hinglish", "english", "hindi","malayalam"]
        else:
            valid_langs = [language]

        # Filtering
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags: tag in tags)) &
            (self.df['language'].isin(valid_langs)) &
            (self.df['length'] == length)
        ]

        return df_filtered.to_dict(orient='records')
    

    def categorize_length(self,line_count):
        if line_count<5:
            return "short"
        elif 5<=line_count<=10:
            return "medium"
        else:
            return "long"
    def get_tag(self):
        return self.unique_tags
if __name__=="__main__":
    fs=Fewshotposts()
    posts=fs.get_filtered_posts("short","hinglish","Job Search")
   
    print(posts)



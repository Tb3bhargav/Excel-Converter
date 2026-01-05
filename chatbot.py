import pandas as pd

class ChatAnalyzer:
    def __init__(self, df):
        self.df = df

    def get_response(self, query):
        """
        Analyzes the query and returns a response based on the DataFrame.
        Supports English and Hindi keywords.
        """
        if self.df is None:
            return "Please convert a chat file first. / कृपया पहले चैट फ़ाइल कनवर्ट करें।"
        
        query = query.lower()
        
        # Intent: Count Messages
        if any(w in query for w in ['count', 'total', 'messages', 'kitne', 'sankhya']):
            total = len(self.df)
            return f"Total messages: {total}\nकुल संदेश: {total}"

        # Intent: Top Sender
        if any(w in query for w in ['sender', 'who', 'kisne', 'bheja', 'top']):
            if 'Sender' in self.df.columns:
                top_sender = self.df['Sender'].value_counts().idxmax()
                count = self.df['Sender'].value_counts().max()
                return f"Top sender is {top_sender} with {count} messages.\nसबसे ज्यादा संदेश {top_sender} ने भेजे हैं ({count})."
            return "Sender information not available."

        # Intent: Media
        if any(w in query for w in ['media', 'photo', 'video', 'image', 'tasveer']):
            media_count = self.df['Message'].str.contains('<Media omitted>', case=False).sum()
            return f"Total media files (omitted): {media_count}\nकुल मीडिया फाइलें: {media_count}"

        # Intent: Busiest Time (Hour)
        if any(w in query for w in ['time', 'busy', 'kab', 'samay', 'hour']):
            if 'Full DateTime' in self.df.columns:
                busy_hour = self.df['Full DateTime'].dt.hour.mode()[0]
                return f"Busiest time is around {busy_hour}:00.\nसबसे व्यस्त समय {busy_hour}:00 बजे के आसपास है।"
            return "Time information not available."

        # Intent: First/Last Message
        if any(w in query for w in ['start', 'end', 'first', 'last', 'shuru', 'khatam']):
            if 'Full DateTime' in self.df.columns:
                start = self.df['Full DateTime'].min()
                end = self.df['Full DateTime'].max()
                return f"Chat started: {start}\nChat ended: {end}\nचैट शुरू: {start}\nचैट समाप्त: {end}"

        return "I didn't understand that. Try asking about 'total messages', 'top sender', or 'busy time'.\nमुझे समझ नहीं आया। 'कुल संदेश', 'किसने भेजा', या 'व्यस्त समय' के बारे में पूछें।"

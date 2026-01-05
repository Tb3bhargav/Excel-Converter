import unittest
import pandas as pd
import os
from parser import WhatsAppParser
from chatbot import ChatAnalyzer

class TestWhatsAppConverter(unittest.TestCase):
    def setUp(self):
        self.parser = WhatsAppParser()
        self.sample_file = 'sample_chat.txt'
        
    def test_parser_txt(self):
        df = self.parser.parse_file(self.sample_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 8) # 8 messages in sample
        
        # Check specific content
        self.assertEqual(df.iloc[0]['Sender'], 'Alice')
        self.assertEqual(df.iloc[3]['Message'], '<Media omitted>')
        
        # Check multiline
        multiline_msg = df.iloc[6]['Message']
        self.assertTrue('multi-line' in multiline_msg)
        
    def test_chatbot(self):
        df = self.parser.parse_file(self.sample_file)
        analyzer = ChatAnalyzer(df)
        
        # Test Count
        resp = analyzer.get_response("count messages")
        self.assertIn("8", resp)
        
        # Test Sender
        resp = analyzer.get_response("who is top sender")
        self.assertIn("Alice", resp) # Alice has 3 messages (0, 2, 7)
        
        # Test Media
        resp = analyzer.get_response("how many media")
        self.assertIn("1", resp)

if __name__ == '__main__':
    unittest.main()

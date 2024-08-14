def getCollections(self):
        import time
        s = time.perf_counter()
        self.chatCollections = sorted(
            self.database.list_collection_names(),
            reverse=True # which should help stack the chat history in ascending order, from bootom to top in QVBoxLayout
        )
        if self.title:
            title = f'{title}' # add timpstamp by dynamic sorting
            self.chatHistory: Collection = self.database[title]
        else:
            if not self.chatCollections or len(self.chatCollections) == 0:
                self.chatHistory = None
            else:
                recentChat = self.chatCollections[-1]
                self.chatHistory: Collection = self.database[recentChat]
        e = time.perf_counter()
        print(f"JanineDB getCollections: {e - s:.2f} seconds")
        return self.chatCollections
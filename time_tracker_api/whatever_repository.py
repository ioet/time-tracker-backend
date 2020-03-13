class WhateverRepository():
    def __init__(self, model_name):
        self.model_name = model_name

    def find_all(self):
        print('Fetching all entries from {0}'.format(self.model_name))
        return []


repository_model = WhateverRepository

class Cluster:
    def __init__(self, firstStream='', stream_array=[]):
        self.streams = []

        if firstStream != '':
            self.streams.append(firstStream)
        else:
            self.streams=stream_array

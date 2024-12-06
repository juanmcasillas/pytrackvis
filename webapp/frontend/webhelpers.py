import json

class JsonResult:
    def __init__(self, status, message):
        self.status = status
        self.message = message

    def response(self):
        return json.dumps({
                'status': self.status, 
                'text': str(self.message)
            }) , self.status


class JsonResultOK(JsonResult):
    def __init__(self, message="OK", status=200):
        super().__init__(status, message)


class JsonResultError(JsonResult):
    def __init__(self, status=500, message="Error"):
        super().__init__(status, message)


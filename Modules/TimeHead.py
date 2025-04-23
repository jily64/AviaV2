import datetime, json

class TimeHead:
    def __init__(self, app):
        self.app = app

        self.zones = []
        self.temp_zones = []
        self.zones_count = 10
        self.headings = []

        self.active_zone = 0
        self.is_active = False

        self.free_zone = datetime.timedelta()

        self.__compile_zones()
        
        self.load()

    def __compile_zones(self):
        self.zones = []
        self.temp_zones = []
        self.headings = []
        for i in range(self.zones_count):
            self.zones.append(datetime.timedelta())
            self.temp_zones.append(None)
            self.headings.append(0)

    def set_active(self):
        self.is_active = not self.is_active

        if self.is_active:
            print(self.temp_zones[0])
            for zone in range(self.zones_count):
                self.temp_zones[zone] = datetime.datetime.now() + self.zones[zone]

    def update(self):
        if not self.is_active:
            return

        if self.zones[self.active_zone] == self.free_zone:
            self.active_zone += 1
            if self.active_zone > self.zones_count - 1:
                self.is_active = False
                self.active_zone = 0

            
            return
        
        if datetime.datetime.now() >= self.temp_zones[self.active_zone]:
            self.active_zone += 1
            if self.active_zone > self.zones_count - 1:
                self.is_active = False
                self.active_zone = 0

    def set_zone(self, id, value, value_type):
        if value_type == "m":

            hours = self.zones[id].seconds // 3600
            minutes = value
        
        elif value_type == "h":

            minutes = self.zones[id].seconds // 60
            hours = value
        
        elif value_type == "hm":
            time = value.split(":")

            try:
                minutes = int(time[1])
                hours = int(time[0])
            except:
                minutes = 0
                hours = 0
        else:
            return
        
        self.zones[id] = datetime.timedelta(minutes=minutes, hours=hours)
        print(self.zones[id], "after")
        self.save()

    def set_heading(self, id, value):
        try:
            self.headings[id] = value
        
        except Exception as e:
            print(e)

        self.save()

    def renew(self):
        self.__compile_zones()
        self.is_active = False
        self.save()

    def load(self):
        with open("heads.json", "r", encoding="UTF-8") as f:
            data = json.load(f)

        if data["zones"] == []:
            for i in self.zones:
                data["zones"].append(i.total_seconds)
        else:
            self.zones = []
            for i in data["zones"]:
                self.zones.append(datetime.timedelta(seconds=i))

        if data["heads"] == []:
            for i in self.headings:
                data["heads"].append(0)
        else:
            self.headings = []
            for i in data["heads"] :
                self.headings.append(i)

    def save(self):
        data = {
            "zones": [],
            "heads": []
        }

        for i in range(len(self.zones)):
            data["zones"].append(self.zones[i].total_seconds())
            data["heads"].append(self.headings[i])

        with open("heads.json", "w", encoding="UTF-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)



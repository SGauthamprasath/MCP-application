from services.weather_service import get_weather
from services.file_service import list_files
from services.csv_service import summarize_csv
import json
from services.csv_service import summarize_csv, filter_csv


weather=get_weather("Mumbai")
#with open("output.json", "w") as f:
   # json.dump(weather, f, indent=4)

files=list_files()
#with open("output.json", "w") as f:
    #json.dump(files, f, indent=4)

summary=summarize_csv("sample.csv")
#with open("output.json", "w") as f:
    #json.dump(summary, f, indent=4)

res=filter_csv("sample.csv", "Category", "Food")

#with open("output.json", "w") as f:
   # json.dump(res, f, indent=4)

json.dump(weather, open("weather.json", "w"), indent=4)
json.dump(files, open("files.json", "w"), indent=4)
json.dump(summary, open("summary.json", "w"), indent=4)
json.dump(res, open("filter.json", "w"), indent=4)

print("Saved to output.json")
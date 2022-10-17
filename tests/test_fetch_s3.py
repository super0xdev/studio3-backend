import requests

session = requests.Session()

result = session.get("https://d3-studio-assets-1660843754077.s3.us-west-1.amazonaws.com/66c7fc_tmp_1665955214_placeholder.e6ee864b2697fa41a66c.png")





with open("./tmp_download/cors_test_1.png", 'wb') as f:
    f.write(result.content)


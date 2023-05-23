import boto3
import streamlit as st
from PIL import Image
import requests
from datetime import datetime

current_time = datetime.utcnow()
s3 = boto3.resource("s3")
bucket = s3.Bucket("employee-photo-bucket-vm-1239")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("media-sharing")

def upload_file(file, file_name, id, tag, description):
    bucket.put_object(Key=file_name, Body=file)
    return f"https://s3.amazonaws.com/{bucket.name}/{file_name}"

def get_item(file_name):
    response = table.get_item(Key={"filename": file_name})
    return response.get("Item")

def create_item(file_name, id, tag, description, url):
    table.put_item(Item={"filename": file_name, "id": id, "tag": tag, "description": description, "url": url})

def update_item(file_name, attribute, value):
    table.update_item(
        Key={"filename": file_name},
        UpdateExpression=f"SET {attribute} = :val",
        ExpressionAttributeValues={":val": value}
    )

def delete_item(file_name):
    table.delete_item(Key={"filename": file_name})

def main():
    st.set_page_config(page_title="Image Uploader", page_icon=":camera:", layout="wide")
    st.title("Image Uploader")

    # Display the contents of the DynamoDB table
    response = table.scan()
    if "Items" in response:
        items = response["Items"]
        st.write("Media sharing table contents:")
        for item in items:
            st.write(f"ID: {item.get('id', '')}")
            st.write(f"Tag: {item.get('tag','')}")
            st.write(f"Description: {item.get('description')}")
            st.write(f"URL: {item.get('url')}")
            st.write("--------")
    else:
        st.write("No items found in media sharing table")

    uploaded_file = st.file_uploader("Choose an image file", type=["jpeg", "png", "jpg"])
    if uploaded_file:
        file_name = uploaded_file.name

        st.write("You selected:", file_name)

        id = st.text_input("Enter ID")
        tag = st.text_input("Enter tag")
        description = st.text_input("Enter description")

        file_path = upload_file(uploaded_file, file_name, id, tag, description)
        st.success("Image uploaded successfully!")
        create_item(file_name, id, tag, description, file_path)

    items = table.scan()["Items"]
    images = []
    for item in items:
        images.append({"filename": item["filename"], "url": item["url"], "id": item["id"], "tag": item["tag"], "description": item["description"]})

    if images:
        st.subheader("Uploaded Images")
        for image in images:
            img = Image.open(requests.get(image["url"], stream=True).raw)
            st.image(img, caption=f"ID: {image['id']}\nTag: {image['tag']}\nDescription: {image['description']}", width=150, use_column_width=False)
            if st.button("View", key=image["filename"]):
                st.image(img, caption=f"ID: {image['id']}\nTag: {image['tag']}\nDescription: {image['description']}", width=600, use_column_width=True)


            if st.button("Delete", key=f"delete_{image['filename']}"):
                delete_item(item["filename"])
                st.warning("Image deleted!")
            # if "thumbnail_url" in item:
            #     img = Image.open(requests.get(item["thumbnail_url"], stream=True).raw)
            #     st.image(img, caption=f"ID: {item['id']}\nTag: {item['tag']}\nDescription: {item['description']}\nThumbnail: {item['thumbnail_url']}", width=150, use_column_width=False)




if __name__ == "__main__":
    main()

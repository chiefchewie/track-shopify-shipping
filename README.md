# Shopify Orders Auto-tracking

Automatically retrieve orders from Shopify and track their shipping status in an Excel sheet\
Working for Python 3.10 as of Jan 2 2022

## Table of Contents

1. [About this project](#about-this-project)
2. [Creating a Shopify private app](#creating-a-shopify-private-app)
3. [Setting up the environment](#setting-up-the-environment)
4. [Running the program](#running-the-program)

## About this project

This is a pure Python program written for my mom, who runs a Shopify store.\
On Shopify, you can't see the shipping status of your orders at a glance. This program automatically tracks shipping information by using the Shopify-provided tracking number and Aftership's powerful API.

## Creating a Shopify private app

Retrieved from [Shopify's page on private apps](https://help.shopify.com/en/manual/apps/private-apps)

### Enabling private apps

Steps:

1. Log-in to your store as the [store owner](#https://help.shopify.com/en/manual/your-account)
2. From your Shopify admin, go to [**Apps**](https://www.shopify.com/admin/apps)
3. Click **Manage private apps.**
4. Click **Enable private apps.**
5. Read and check the terms, and then click **Enable private app development**.

### Generating private app credentials

1. From your Shopify admin, go to [**Apps**](https://www.shopify.com/admin/apps)
2. Click **Manage private apps.**
3. Click **Create private app.**
4. In the **App details** section, enter a name for your private app and a contact email address. Shopify uses the email address to contact the developer if there is an issue with the private app, such as when an API change might break it.
5. In the **Admin API** section, select the areas of your store that you want the app to be able to access.
6. Click **save.**

## Setting up the environment

### System Requirements

|        |            |
| ------ | ---------- |
| OS     | Windows 10 |
| Python | 3.10       |

### Environment variables

Create a .env file in the same directory as main.py and place these key-value pairs in them

| Variable  | Description                 |
| --------- | --------------------------- |
| API_KEY   | Your private app's API key  |
| PASSWORD  | Your private app's password |
| SHOP_NAME | The name of your shop       |

## Running the program

Simply run the Python script. Example:

```shell
python main.py
```

### Notes

-   The output Excel is located at /output and named `orders.xlsx`
-   There are many attributes not captured by this program
-   Check out Shopify Developer's [documentation](https://shopify.dev/api/admin-rest/2021-10/resources/order#top) for the `Order` object and add any keys to the `useful_keys` list if you want them

Thanks for stopping by and checking out my program!

# persona-dashboard

Personas are fictional characters that represent a segment of a company's customer base. They are one of the most popular marketing tools used today. In a time where people receive tens of emails per day, personas create PERSONAlization that allows companies to get through to customers. 

Leading marketing automation platforms, such as Pardot, do not have built-in visualizations to monitor the health of personas or any customer segments.

This full-stack analytics application leverages the Pardot API as well as Amazon’s RDS and EC2 services, to help companies track their personas’ growth and engagement.

![](https://media.giphy.com/media/lOmuezZPD9sdYpc0NB/giphy.gif)

## ETL Flow
1. Jupyter Notebook Server to an Amazon EC2 Instance. Rather than run Jupyter locally, an EC2 instance offers the ability to upgrade computing power and run a script anytime.
2. Python script that extracts data from Pardot and Salesforce, transforms it, and loads it to a PostgreSQL database. And, that scripts runs on business days at 12 am when my computer is off and I’m asleep.
3. Once you have your instance set up, you can open it up in a browser and upload a python file. The file for this application is called
4. Now in Git Bash or a similar application, you can connect to your instance.

```
cd dev/jupyter
ssh ubuntu@34.201.49.60 -i JupyterKey.pem
```
5. use cron to schedule scripts to run periodically. So we could change this one to run every 15 minutes or whatever we like.

6. Loading the data to a SQL database is important because we want our web application to be fast so rather than have the application connect directly to the Salesforce and Pardot APIs, the data in the SQL database is already simplified so it can be retrieved and plotted quickly.

7. On the front end, you have your usual suspects which are hosted on Heroku.


### Technology Stack
<img src= "https://github.com/JohnvanZalk/persona-dashboard/blob/master/images/technology_diagram.JPG" width="700">

## To be continuted...
Right now, this application is built for a single organization, but my goal is to redesign it so that any company can connect to their Pardot environment and get insights.


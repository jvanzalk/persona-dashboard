# persona-dashboard

Personas are fictional characters that represent a segment of a company's customer base. They are one of the most popular marketing tools used today. In a time where people receive tens of emails per day, personas create PERSONAlization that allows companies to get through to customers. 

Leading marketing automation platforms, such as Pardot, do not have built-in visualizations to monitor the health of personas or any customer segments.

This full-stack analytics application leverages the Pardot API as well as Amazon’s RDS and EC2 services, to help companies track their personas’ growth and engagement.

https://persona-dashboard.herokuapp.com/

## Technology Stack
<img src= "https://github.com/JohnvanZalk/persona-dashboard/blob/master/images/technology_diagram.JPG" width="700">

1. A Jupyter Notebook Server on an Amazon EC2 Instance.
2. A Python script hosted on the server extracts data from Pardot and Salesforce, transforms it, and loads it to a PostgreSQL database. The script is scheduled to run on business days at 12 am. Code in git bash:

```
cd dev/jupyter
ssh ubuntu@34.201.49.60 -i JupyterKey.pem
crontab -e
0 0 * * 1-5 python3 personas_to_sql.py 
```

6. The flask application retrieves data from the SQL database rather than connecting directly to Salesforce and Pardot so data can be plotted quickly.

7. The flask application plus frontend code are hosted on Heroku.

## To be continuted...
Right now, this application is built for a single organization, but my goal is to redesign it so that any company can connect to their Pardot environment and get insights.


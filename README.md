# persona-dashboard

Personas are fictional characters that represent a segment of a company's customer base. They are one of the most popular marketing tools used today. In a time where people receive tens of emails per day, personas create PERSONAlization that allows companies to get through to customers. 

Leading marketing automation platforms, such as Pardot, do not have built-in visualizations to monitor the health of personas or any customer segments.

This full-stack analytics application leverages the Pardot API as well as Amazon’s RDS and EC2 services, to a company track their personas’ growth and engagement.

https://persona-dashboard.herokuapp.com/

## Technology Stack
<img src= "https://github.com/JohnvanZalk/persona-dashboard/blob/master/images/technology_diagram.JPG" width="700">

1. A Jupyter Notebook Server on an Amazon EC2 Instance. This server hosts a python script that extracts data from Pardot and Salesforce, transforms it, and loads it to a PostgreSQL database. Using crontab, the script is scheduled to run on business days at 12 am.
2. The flask application retrieves data from the SQL database rather than connecting directly to Salesforce and Pardot. This increases performance by allowing plots to render more quickly.
3. The flask application plus frontend code are hosted on Heroku.

## Future Development
Right now, this application is built for a single organization, but my goal is to scale it so that any company can connect to their Pardot environment and get insights.


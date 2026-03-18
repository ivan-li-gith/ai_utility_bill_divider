# AI Utility Bill Divider

An AI-powered web application designed to automate the process of parsing utility bills and calculating fair monthly splits among roommates.

## Live Demo
Access the application here: [AI Utility Bill Divider](http://18.221.131.243/)

### Guest Access
To explore the application without affecting personal production data, please use the following credentials:
* **Username:** `guest`
* **Password:** `guest`
  
## Key Features
* **AI Data Extraction**: Automatically parses PDF bills to find service dates and amounts due using the OpenAI API.
* **Dynamic Roommate Management**: Add or remove roommates directly within the upload workflow to adjust splits.
* **Automated Rollover Tracking**: Automatically carries over unpaid balances to the next month's total for each individual.
* **Interactive History**: A dashboard to review past bills, track payment status, and visualize monthly spending trends.

## Technical Stack
* **Frontend**: Streamlit
* **AI Engine**: OpenAI GPT-4o
* **Database**: MySQL hosted on AWS RDS
* **Infrastructure**: Deployed on AWS EC2
* **Libraries**: SQLAlchemy, Pandas, PyMuPDF (fitz), Python-Dotenv

## How to Use
1.  **Login**: Use the `guest` credentials provided above.
2.  **Manage Roommates**: Open the "Manage Roommates" expander to add the people you are splitting with otherwise, it will just be yourself.
3.  **Upload Bills**: Drag and drop your utility PDF statements into the uploader.
4.  **Review**: Verify the AI-extracted data in the interactive data editor and click "Confirm & Save".
5.  **Track Payments**: Switch to the "History & Payments" tab to mark bills as "Paid" and see how it affects next month's totals.

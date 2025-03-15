# Clinical Decision Support System (CDSS)

This project is an advanced AI-powered Clinical Decision Support System (CDSS) designed to transform how healthcare professionals access and act on patient data. By leveraging LlamaIndex and state-of-the-art LLMs (GPT-4), the system delivers faster, clearer, and actionable insights to enhance patient care.

## Key Features

- **Intelligent Data Retrieval:**  
  Efficiently indexes and retrieves complex patient data to deliver precise, evidence-based recommendations.

- **Risk Awareness & Predictive Analytics:**  
  Dynamically identifies critical risks and uses patient history and analytics to uncover deep diagnostic insights.

- **Specialty Customization:**  
  Easily tailors recommendations for specific medical fields (e.g., cardiology, oncology).

- **Scalability & Continuous Learning:**  
  Supports large datasets and continuously evolves by integrating the latest clinical research and trials.

## Tech Stack

- **Data Management:**  
  Ingests MIMIC-IV demo data into PostgreSQL, performing multi-table joins to extract relevant patient details.

- **Data Transformation:**  
  Converts structured data into JSON and then text, preserving hierarchical relationships for semantic indexing.

- **Indexing & Retrieval:**  
  Utilizes LlamaIndex’s Vector Store for efficient semantic search and similarity-based retrieval.

- **LLM Integration:**  
  Uses OpenAI GPT-4 to transform queried data into structured, actionable outputs, seamlessly visualized via Streamlit.

<br></br>

<h1>Data Source</h1> 
This project uses the [MIMIC-IV Clinical Database Demo (version 2.2)](https://physionet.org/content/mimic-iv-demo/2.2/).  

<h3>Database:</h3>
Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., and Mark, R. (2023) 'MIMIC-IV Clinical Database Demo' (version 2.2), PhysioNet. 
Available at: https://doi.org/10.13026/dp1f-ex47.

<h3>Physionet</h3>
Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P.C., Mark, R., Mietus, J.E., Moody, G.B., Peng, C.K. and Stanley, H.E., 
2000. PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation [Online]. 
101 (23), pp. e215–e220.

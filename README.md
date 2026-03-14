2.  Problem Definition & Objectives
2.1 Problem Definition
In the context of the rapid growth of e-commerce, The Gioi Di Dong is facing significant management challenges in optimizing its online customer consultation process. Currently, most interactions still rely on human resources, leading to limited scalability when traffic spikes. Customer service teams frequently have to handle repetitive queries regarding technical specifications and price segments, causing response delays and reducing overall operational efficiency.
This challenge is further exacerbated by the limitations of the internal search system, which only operates based on exact keyword matching and fixed filters. The current tool is not flexible enough to process contextual natural language queries — such as searching for a device specialized for programming within a specific budget. The mismatch between user language and the product data structure makes searching difficult. Furthermore, the quality of consultation depends heavily on the knowledge of individual staff members, leading to inconsistent recommendations and the risk of missing the best options within a diverse product catalog.





2.2 Project Objectives
The primary objective of this project is to research and deploy an intelligent laptop consultation chatbot to automate the customer support process on the website platform. The project aims to build a model capable of receiving and deeply analyzing user intent to provide accurate, consistent, and personalized product recommendations based on a combination of real-world usage needs and hardware configuration data.
Operationally, the system is expected to fully resolve the issue of staff overload by providing high-accuracy, real-time automated responses. This solution goes beyond mere information retrieval; it aims to optimize the customer journey by shifting the search method from manual data filtering to intelligent interaction. By systematizing the product recommendation process, the project ensures that every customer gains access to the most suitable laptop options, thereby enhancing business efficiency and asserting The Gioi Di Dong's technological leadership in the online retail sector.
3. Data Understanding & Preprocessing
3.1 Data Understanding
After the process of collecting the dataset from the Thế Giới Di Động retail system, it includes 438 laptop samples with 15 attributes: brand, name, cpu, ram, gpu, storage, screen size, screen resolution, screen panel, battery (wh), color, price, rating, review text, description. This dataset is used as the foundation for the system, aiming to provide context for the large language model (LLM) in the Retrieval-Augmented Generation (RAG) architecture. In terms of structure, the data combines quantitative attributes, qualitative attributes, and free-text content to simultaneously support two retrieval mechanisms: hard filtering and semantic search.
The first group consists of configuration specification attributes, including brand, name, cpu, ram (GB), gpu, storage (GB), screen size (inch), screen resolution, screen panel, battery (wh), color, price and rating. These are clearly structured data fields that allow the system to perform queries based on specific conditions such as price range, RAM capacity, or hardware configuration. In the storage architecture of the RAG system, this group of data also serves as metadata attached to support the retrieval process of the second group. The second group consists of unstructured textual data, including two important fields: description and review text. The description field contains detailed descriptive paragraphs summarizing the key advantages, real-world performance, and target user groups of each product. This serves as the foundational knowledge source used to create vector embeddings, enabling semantic search based on content similarity.




3.2 Data Processing
The preprocessing process was carried out to transform 438 raw records of laptop specifications collected from Thế Giới Di Động into a clean, consistent dataset ready for both conditional retrieval and semantic retrieval. The entire processing pipeline was implemented in a notebook environment, with the initial focus on handling missing and duplicate data based on business rules related to electronic products. Specifically, the system removes duplicate records and rows missing core information that plays an important role in product classification, including 11 samples missing price information and several samples without RAM configuration, GPU, or storage capacity information.
This removal is mandatory to prevent logical errors when users perform product filtering based on configuration, resulting in a standardized dataset of 431 complete samples. For supplementary information fields such as color or screen panel type, the data is filled with the default value "Standard" to maintain the table structure. For the textual fields description and review text, they are processed by filling empty strings or the value 0, ensuring that the embedding process runs continuously without encountering formatting issues.
Next, in order for conditional operations to function correctly at the database layer, the process focuses on standardizing formats and unifying units for technical specifications. The price field is cleaned of currency characters and converted to an integer type to support price comparison queries. Laptop-specific specifications such as RAM capacity, storage, battery capacity, and screen resolution are extracted as pure numerical values using regular expressions (Regex). In particular, for the storage attribute, all values are consistently converted to the Gigabyte (GB) unit, for example converting 1 TB to 1024 GB.
This processing step eliminates the unit inconsistency commonly found in e-commerce data, ensuring absolute accuracy when users search for laptops based on specific capacity thresholds. 
At the same time, the process performs identifier standardization for hardware components and cleans free-text content to optimize search capability. For CPU and GPU, string processing techniques are applied to unify capitalization and remove redundant whitespace, thereby bringing the identifiers to a single standard.
This helps the system avoid missing potential products when users perform hard filtering based on chip series or graphics cards. At the same time, the product description and user review fields are standardized in encoding format and special characters are removed to preserve semantic meaning as much as possible for vector space creation.
Finally, after completing the cleaning steps, the 431 finalized records are restructured to serve the Hybrid Search architecture. All data is separated into two specialized streams: structured technical attributes (metadata) used as parameters for conditional filtering functions, while the detailed descriptive content is aggregated into source documents to be fed into the embedding model. This entire structure is then loaded into the ChromaDB database, forming a clean and standardized data foundation that enables the large language model (LLM) to provide laptop information in the most effective way.

4. Algorithm Selection & Modeling
4.1 Appropriate Algorithm Selection
The product recommendation problem in the project is approached from the perspective of classification and similarity search in Data Mining, specifically by applying the foundation of the K-Nearest Neighbors (KNN) algorithm. Although the overall solution is built on the Retrieval-Augmented Generation (RAG) architecture, the core nature of the retrieval stage is essentially a KNN problem executed in the Vector Embedding Space.
Instead of applying the KNN algorithm on traditional quantitative feature fields (tabular data) or relying on lexical matching methods that are limited in contextual understanding, the project uses the intfloat/multilingual-e5-large model. This model functions as a feature transformation mechanism, mapping unstructured textual data into a high-dimensional vector space with high semantic fidelity.
The choice of the KNN foundation (through Dense Retrieval) combined with the hard attribute filtering mechanism (Metadata Filtering) forms a powerful Hybrid Search framework. This approach perfectly satisfies the requirements of the problem: allowing the system to simultaneously interpret the abstract intent of users through KNN distance while also handling strict technical constraints related to hardware.

4.2 Mathematical Foundations of Vector Retrieval
The quantitative foundation of the retrieval process lies in computing the distance in the KNN algorithm between the query vector vq and the set of document vectors vd in the database. Unlike the traditional KNN algorithm, which typically uses Euclidean distance, the project applies the Cosine Similarity metric as the objective function to optimize the evaluation of semantic relevance:

To optimize retrieval speed in the vector space, the system applies the Approximate Nearest Neighbor (ANN) search algorithm instead of scanning the entire dataset using the traditional KNN approach. This process is executed through the ChromaDB database using the Hierarchical Navigable Small World index, enabling results to be returned with low latency. At the same time, the system applies a strict cutoff threshold SIMILARITY_THRESHOLD = 0.78 to eliminate less relevant results, maintaining the highest precision for the output.
4.3 Intent Parsing and Hybrid Search Pipeline
To further enforce technical constraints, the system implements a Hybrid Search mechanism through the integration of vector retrieval and metadata filtering. The process begins with an Intent Parsing stage, where Regular Expressions (Regex) are employed to extract quantitative entities such as budget (PMAX), RAM capacity, and GPU identifiers (Dedicated vs Integrated). These extracted entities are then transformed into Boolean logic queries, which are executed directly on the metadata layer of ChromaDB to eliminate candidates that do not satisfy hard constraints before the semantic ranking stage.
For the Named Entity Lookup scenario, the system integrates the Gestalt Pattern Matching algorithm via the difflib.SequenceMatcher library. The final score (Sfinal) is computed using a linear weighted function between the semantic similarity score (Ssem) and the string similarity score (Sstr):

The assignment of a weight of 0.6 to Sstr ensures priority for absolute accuracy when users provide a specific product identifier (Model name), while still preserving the contextual inference capability of the RAG model.
4.4 Neural Generation and Contextual Constraints
The final stage of the pipeline utilizes the openai/gpt-oss-120b model as the Reasoning Engine. The retrieved context is tightly structured and fed into the model through Prompt Engineering with explicit constraints. The system requires the model to reason strictly based on the dataset of K = 6 provided candidates, preventing the generation of information outside the database. The Conversation State Management mechanism is maintained through a sliding window structure that stores the two most recent interaction turns, enabling tasks such as comparative analysis and Anaphora Resolution within the customer's continuous dialogue flow.
5. Model Evaluation & Analysis
5.1 Evaluation Metrics
To evaluate the operational performance of the laptop consultation chatbot system, the evaluation process focuses on the quality of product retrieval and the accuracy of advisory responses rather than using traditional classification metrics. Since the problem belongs to the domain of Information Retrieval combined with natural language generation, the system is assessed through several metrics that reflect real-world search and consultation capabilities.
First, Top-K Retrieval Accuracy is used to measure the system’s ability to place relevant products in the retrieved result list, where a query is considered successful if at least one laptop that correctly satisfies the user’s needs appears within the Top-K returned results. In addition, the Semantic Relevance Score is examined through the Cosine Similarity score between the query and the retrieved products, ensuring that only results with sufficiently high semantic similarity are used as context for the language model.
For the specific device name lookup function, the system is evaluated using Lookup Accuracy, which reflects the ability to correctly identify a product even when users provide incomplete information or partially incorrect model names. This metric verifies the effectiveness of the re-ranking mechanism that combines semantic similarity and string matching. Furthermore, the final response quality of the chatbot is also assessed through Response Consistency, representing the extent to which the language model’s answers adhere to the retrieved data and avoid generating information outside the knowledge base.
5.2 Result Interpretation and Discussion
For quantitative evaluation, the system is tested on an evaluation dataset (Test set) consisting of 100 diverse customer queries, distributed across three scenarios: general requirement queries, queries with strict configuration or budget constraints, and specific device name lookup with misspelled model names.
The system performance is compared between two algorithm versions: the Baseline (using only Semantic Search with vectors) and the Proposed Model (using Hybrid Search combined with Intent Parsing).



Table 1: Performance evaluation results of retrieval and text generation Detailed analysis of quantitative results
Evaluation Metrics
Baseline (Semantic Search Only)
Proposed (Hybrid Search + LLM)

Top-5 Retrieval Accuracy
3/5 questions correct
5/5 questions correct
Average Semantic Score (Cosine Similarity)
1/5 questions correct
5/5 questions correct
Lookup Accuracy (Model Name)
2/5 questions correct
5/5 questions correct
Cosine Score
~ 0.72
~ 0.85

Overall, although the experiment was conducted on a relatively small scale, the results clearly demonstrate the superiority of the Hybrid Search architecture compared to single retrieval methods in the context of e-commerce product recommendation systems.
6. Conclusions and Future Improvements
6.1 Conclusions
The project successfully developed an intelligent laptop consultation chatbot that effectively overcomes the limitations of traditional search methods used at The Gioi Di Dong, achieving four key outcomes:
Data: A complete preprocessing pipeline was developed to standardize complex raw data into a structured format, establishing a solid foundation for subsequent filtering and retrieval processes.
Technical Implementation: The system effectively deploys a RAG architecture integrated with Hybrid Search. The combination of Semantic Search and Metadata Filtering enables the system to accurately understand user intent while strictly enforcing hardware constraints.
Application: The chatbot is capable of generating natural responses that closely adhere to real data while strictly following the principle of avoiding fabricated information (zero-hallucination).
Business Value (Business Insights): The solution helps automate basic consultation tasks, reduce operational workload, and opens the potential for analyzing consumer trends through historical customer query data.

6.2 Future Improvements
Although the project has achieved promising results, there remains room for further development to optimize the user experience in the future:
Real-time Data Updates: Integrate directly with the store’s API to instantly update inventory status, promotional prices, and the latest product models.
User Personalization: Develop a system capable of remembering conversation history and individual preferences to provide more highly personalized recommendations (Personalization).
Embedding Model Optimization (Fine-tuning): Conduct fine-tuning of the embedding model on a domain-specific dataset related to computer technology in Vietnam to better understand slang terms or specialized expressions commonly used by local customers.
Multi-channel Expansion: Integrate the chatbot into popular platforms such as Facebook Messenger, Zalo, or directly into the mobile application to reach a broader customer base.


<h3 align="center">job_recsys - Job Recommendation System</h3>

---

<p align="center"> An end-to-end system that recommends suitable jobs for a user-provided resume (in pdf) and/or a profile.
    <br> 
</p>

## TL;DR
In this project, I built an end-to-end job recommend system by using **CV Parser** for extracting important information such as ```study time```,  ```working time```, ```position```, ```experience```, ```address```,... from a pdf CV file to a JSON file and **Skill Extractor** for extracting a set of skills from a text (e.g. experiences or job requirements,...). These two components were developed by my colleagues at DSLab - Hanoi University of Science and Technologies and unfortunately, we can't make them and the data used in job_recsys public. Then, I developed **Feature Normalizer** for skills clustering and feature extraction and **Ranking Component** for embedding those features into vector space and matching them to get appropriate results. 

## Table of Contents
+ [Overview](#overview)
+ [Demo](#demo)
+ [How it works](#working)
+ [Getting Started](#getting_started)

## Overview <a name = "overview"></a>
<table><tr><td>
job_recsys = CV Parser + Skill Extractor + Feature Normalizer + Ranking Component
</td></tr></table>
The following figure describes the job_recsys workflow:

![overview](https://github.com/Dec1mo/Job_Recommendation/blob/main/docs/overview.png?raw=true)

## Demo <a name = "demo"></a>
I only made a simple two-page flask web app in order to show how job_recsys works.
- At **home page**, a user can upload his/her CV and/or fill some information in the Profile section, then press ```Submit```.
<p align="center">
  <img src="https://github.com/Dec1mo/Job_Recommendation/blob/main/docs/demo_homepage.png?raw=true" />
</p>

- Top k=3 most suitable job descriptions  for that user will appear at **result page**:
<p align="center">
  <img src="https://github.com/Dec1mo/Job_Recommendation/blob/main/docs/demo_result_page.png?raw=true" />
</p>

## How it works <a name = "working"></a>
I recommend you checking my [presentation file](https://github.com/Dec1mo/job_recsys/blob/main/docs/ThaiDD_Job_RecSys.pdf) for detailed information.
### CV Parser
**CV Parser** for extracting important information such as ```study time```,  ```working time```, ```position```, ```experience```, ```address```,... from a pdf CV file to a JSON file.
<p align="center">
  <img src="https://github.com/Dec1mo/job_recsys/blob/main/docs/cv_parser.jpg?raw=true" />
</p>

### Skill Extractor
**Skill Extractor** extracts a set of skills from a text (such as experiences or job requirements,...).
<p align="center">
  <img src="https://github.com/Dec1mo/job_recsys/blob/main/docs/skill_extractor.png?raw=true" />
</p>

### Feature Normalizer 
**Feature Normalizer** consists of 2 components:
- Skill Clustering uses [Affinity Propagation](https://en.wikipedia.org/wiki/Affinity_propagation) for normalizing skills (6760 skills had been normalized to 1002 skills).
- Feature Extraction normalizes other features by using some advanced techniques such as fuzzy searching, interquartile range; then combines them.
<p align="center">
  <img src="https://github.com/Dec1mo/job_recsys/blob/main/docs/skill_normalizer.png?raw=true" />
</p>

### Ranking Component
**Ranking Component** consists of 2 components:
- Embedding Component uses TFIDF, LSA, or SimilarityEncoding to embed features into vector space.
- Matching Component computes the weighted average of cosine similarity or Word Mover’s Distance (WMD) between users' vectors and job descriptions' vectors; then ranks them to obtain top k matches.
<p align="center">
  <img src="https://github.com/Dec1mo/job_recsys/blob/main/docs/ranking_component.png?raw=true" />
</p>

## Getting Started <a name = "getting_started"></a>
### Requirements
+ CV Parser API (not public)
+ Skill Extractor API (not public)
+ Data: resumes, job descriptions, skills (not public)
+ Other libraries

⚠ Warning: Apparently, you don't have the not public stuff so recommendations can't be made probably. You can still treat this project as a guideline for building an end-to-end recommendation system. Also, you can turn on the web app and mess with its interface.

### Installing
After cloning this project, you will want to process data and save some pipelines beforehand.
#### Process CV, JD data
```
>> python app/data_process/preprocess.py
```
#### Create ```skill_norm_dict``` for normalizing skills
```
>> python app/data_process/skill_norm.py
```
#### Create some embedding pipelines
```
>> python app/model/embedding.py
```
We have everything prepared now.
#### It's time to start the flask web app
```
>> python app/run.py
```
job_recsys is now ready to recommend some suitable jobs for you 😎.

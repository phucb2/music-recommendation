# Music Recommendation System — Final Report
<!-- Course assignment report: Intelligent System, AY 2025–2026. Covers full pipeline from theory to evaluation. -->

**Vietnam National University Ho Chi Minh City**
**Ho Chi Minh City University of Technology**
**Faculty of Computer Science and Engineering**
**Intelligent System — Recommendation System**

Instructor: Quang Thanh Tho
Students: Luu Trong To — 2570802 | Bui Ba Phuc — 2570799 | Nguyen Ba Nam — 2570795

Ho Chi Minh City, May 2026

---

## Contents

1. [Introduction to Recommender Systems](#1-introduction-to-recommender-systems)
2. [Stakeholders and Potential Benefits](#2-stakeholders-and-potential-benefits)
3. [Theoretical Background](#3-theoretical-background)
4. [Dataset Description and Preprocessing Steps](#4-dataset-description-and-preprocessing-steps)
5. [System Design](#5-system-design)
6. [AI Pipeline for Data Training and Deployment](#6-ai-pipeline-for-data-training-and-deployment)
7. [Evaluation Results](#7-evaluation-results)
   - 7.5 ANN Retrieval Benchmark
   - 7.6 Discussion

---

## 1 Introduction to Recommender Systems

Recommender systems are software tools that help users discover items they are likely to find useful or interesting. In practice, they act as intelligent assistants that analyze user behavior, preferences, and available content in order to suggest relevant products, movies, music, videos, articles, or other digital items. Instead of forcing users to manually search through a huge collection of choices, a recommender system narrows the search space and presents a small set of meaningful options.

The need for recommender systems has become increasingly important in the digital era because modern online platforms contain an enormous number of items. E-commerce websites such as Amazon, streaming services such as Netflix, and content platforms such as YouTube provide users with millions of alternatives. Although such variety is beneficial, it also creates the problem of information overload. Users may spend too much time searching, may overlook suitable items, or may repeatedly select only the most obvious choices.

This challenge is closely related to the Long Tail phenomenon. In online environments, a small number of items receive most of the attention, while a very large number of niche items remain difficult to discover. A well-designed recommender system helps connect users with these less popular but highly relevant items, thereby improving user satisfaction and increasing the visibility of the full catalog.

> **Example: Long Tail Effect in Practice.** A classic case is the book *Touching the Void*. Years after its original release, the book became a bestseller again because recommendation algorithms linked it to the newer and more popular title *Into Thin Air*. This example shows how recommender systems can revive interest in older or niche items by connecting them with popular products through user behavior and association patterns.

From the user perspective, recommender systems save time, reduce effort, and improve decision making. From the business perspective, they increase engagement, improve retention, support personalization, and can significantly boost sales or content consumption. For these reasons, recommender systems have become an essential component of many modern intelligent applications.

### 1.1 Types of Recommendations

Recommendation approaches can be divided into two broad categories depending on whether the suggestions are tailored to individual users.

#### 1.1.1 Non-Personalized Recommendations

Non-personalized recommendation methods provide the same suggestions to every user without considering individual preferences, history, or behavior. Common examples include:

- **Editorial and hand-curated lists**: recommendations prepared by humans, such as "Top Picks" or "Editor's Choice," where experts decide which items should be highlighted.
- **Simple aggregates**: recommendations based on overall popularity, such as "Most Popular," "Trending," or "Top 10" lists.

These methods are easy to implement and useful for presenting broadly attractive items. However, they are limited because they do not reflect personal interests and therefore do not help users discover less well-known items that may better match their tastes.

#### 1.1.2 Personalized Recommendations

Personalized recommendation systems are customized for each user. They analyze user behavior, such as what a person watches, clicks, rates, or buys, in order to suggest items that are more relevant to individual interests. Because these systems take personal preferences into account, they are generally more effective than non-personalized methods at helping users discover suitable content.

The main personalized recommendation approaches include:

- **Content-based systems**: these methods recommend items that are similar to those a user has liked before. For example, if a user often watches action movies, the system may suggest other action films with related themes, genres, or actors.
- **Collaborative filtering**: these methods recommend items based on the preferences of similar users. If users with tastes similar to a target user enjoyed a particular movie or product, the system may recommend that item as well.
- **Knowledge-based and hybrid systems**: knowledge-based methods use explicit information about user needs and item characteristics, which is useful in domains such as cars, houses, or financial products. Hybrid systems combine multiple recommendation techniques to improve accuracy and to address challenges such as limited data for new users or new items.

### 1.2 Short Case Study: Netflix Recommendations

Netflix provides a clear real-world example of how different recommendation strategies are used in the same platform.

**Non-Personalized Recommendations on Netflix:**
- "Top 10 phim tại Việt Nam hôm nay": driven by national viewing trends and regional popularity.
- "Xem lại" (Continue Watching): a simple rule-based strategy that re-surfaces unfinished content.

**Personalized Recommendations on Netflix:**
- "Danh sách của tôi" (My List): contains movies and shows the user has saved manually.
- "Vì bạn đã xem…" (Because you watched…): recommends titles related to previous viewing behavior.
- "Đề xuất cho bạn" (Recommended for you): deeper personalization by combining viewing history with patterns learned from users with similar preferences.

### 1.3 The Foundational Framework: The Utility Matrix

The core of any recommendation system is the utility matrix, which records how useful or desirable each item is for each user. Formally, the recommendation task can be defined as a utility function:

$$u: X \times S \rightarrow R$$

where:
- $X$ is the set of customers or users,
- $S$ is the set of items such as products, news articles, movies, or videos,
- $R$ is the set of ratings or utility values, for example a score from 1 to 5 or a normalized value in [0, 1].

In practice, this function is represented as a matrix in which rows correspond to users and columns correspond to items. Each entry stores the observed or estimated preference of a user for a particular item. The central technical challenge in this framework is **sparsity**. In large-scale real systems, the utility matrix is overwhelmingly incomplete because most users interact with only a tiny fraction of the available catalog. As a result, most entries are unknown.

The goal of a recommender system is therefore not to fill the entire matrix perfectly. Instead, it aims to extrapolate the unknown entries that are likely to have high utility and then recommend those items to the appropriate users.

#### 1.3.1 Representing the Utility Matrix

**Table 1: A simple example of a utility matrix.**

| | Item A (Metallica) | Item B (Megadeth) | Item C (Into Thin Air) |
|---|---|---|---|
| User 1 | 5 | ? | 1 |
| User 2 | ? | 4 | ? |
| User 3 | 4 | 5 | ? |

#### 1.3.2 Data Collection Strategies

To build and update the utility matrix, recommendation systems rely on two main forms of feedback.

- **Explicit ratings**: users provide direct evaluations such as star ratings, likes, scores, or written reviews. These signals are usually high quality because they clearly reflect user intent. However, they suffer from data scarcity because many users do not want to spend extra effort rating items regularly.
- **Implicit ratings**: the system infers utility from user behavior, including clicks, purchases, watch time, dwell time, search activity, or repeated consumption. Although these signals are noisier than explicit ratings, they are extremely valuable in modern machine learning systems because they can be collected continuously at scale without increasing user friction.

In this report, the main focus is on collaborative filtering. The following discussion therefore concentrates on collaborative filtering methods, examples, and evaluation, while other recommendation paradigms are introduced only for context.

---

## 2 Stakeholders and Potential Benefits

This music recommendation system involves three primary stakeholder groups, each with distinct roles and benefits derived from the project.

### 2.1 End Users (Listeners)

End users are subscribed users who interact with the platform daily through two main surfaces: the **Homepage** and the **Player**. They have an existing listening history and provide both implicit feedback (play duration) and explicit feedback (like/dislike) to the system.

**Potential Benefits:**
- **Personalized Music Discovery.** The homepage recommendation surface delivers curated song suggestions tailored to each user's individual taste, enabling them to discover new music that aligns with their preferences without manual searching.
- **Seamless and Uninterrupted Listening Experience.** The next-song recommendation feature uses song-to-song similarity to suggest a contextually appropriate follow-up track, ensuring continuous playback and reducing drop-off between songs.
- **Increased Subscription Value.** By receiving a genuinely personalized experience, users gain greater satisfaction from their subscription, reinforcing long-term retention and platform loyalty.
- **User Control Through Feedback.** The like/dislike mechanism gives users direct influence over future recommendations, creating a personalized feedback loop that improves recommendation quality over time.

### 2.2 Data Scientists

Data scientists are responsible for designing, training, evaluating, and iterating on the machine learning models that power the recommendation engine. They operate at the core of the system's intelligence layer.

**Potential Benefits:**
- **Access to Rich and Structured Behavioral Data.** The system's event logging infrastructure captures fine-grained user interaction data — including play duration, play events, likes, and dislikes — providing both implicit and explicit signals necessary for building and validating recommendation models.
- **Support for Iterative Model Development.** The system architecture supports periodic model refresh and is designed with training and evaluation logging in mind, enabling data scientists to continuously experiment with new approaches and measure their real-world impact.
- **Modular and Scalable Pipeline.** The clear separation of components — candidate generation, ranking, and recommendation serving — allows data scientists to improve individual stages independently without disrupting the overall system, reducing iteration cost and deployment risk.
- **Measurable and Reproducible Evaluation.** Because all key interaction metrics are persisted in the backend database, data scientists can run offline evaluations and compare model versions against consistent historical data, supporting evidence-based decision-making.

### 2.3 Project Managers

Project Managers oversee the end-to-end delivery of the recommendation system, coordinating between engineering, data science, and product teams. They are responsible for defining success metrics, tracking business impact, and ensuring the system delivers measurable value aligned with organizational goals.

**Potential Benefits:**
- **CTR as a Primary KPI.** Click-Through Rate (CTR) — the ratio of users who click on a recommended song to the total number of recommendations displayed — serves as a direct, quantifiable measure of recommendation relevance. CTR is formally defined as:

$$\text{CTR} = \frac{\text{Number of Recommendation Clicks}}{\text{Total Recommendations Displayed}} \times 100\%$$

- **Data-Driven Decision Making.** With CTR tracked per recommendation surface (Homepage vs. Next-song), Project Managers can identify which surface delivers stronger engagement and prioritize engineering resources accordingly.
- **Iteration and Release Governance.** CTR trends across model versions provide objective criteria for approving or rolling back releases.
- **Business Impact Visibility.** An improvement in CTR directly correlates with increased listening time, lower churn, and higher subscription retention.
- **Balancing Quality vs. Quantity.** By pairing CTR with play duration data, Project Managers can ensure the system optimizes for genuine engagement rather than superficial clicks.

### 2.4 Summary

**Table 2: Stakeholder Summary**

| Stakeholder | Role | Primary Benefit |
|---|---|---|
| End Users (Listeners) | Consume recommendations | Personalized discovery & seamless playback |
| Data Scientists | Build & improve ML models | Rich data, modular pipeline, reproducible evaluation |
| Project Managers | Govern delivery & measure impact | CTR-driven KPIs, release governance, business visibility |

---

## 3 Theoretical Background

This section presents the theoretical foundations underlying the music recommendation system, covering the two principal algorithmic paradigms employed: **Content-Based Filtering** and **Collaborative Filtering**.

### 3.1 Content-Based Filtering with K-Nearest Neighbors (KNN)

#### 3.1.1 Overview

Content-based filtering recommends items to a user based on the intrinsic attributes of the items themselves, rather than the behavior of other users. The core assumption is that a user who enjoyed a particular item will likely enjoy other items with similar characteristics.

In the context of this music recommendation system, each song is represented as a feature vector composed of its metadata and audio attributes, including:

- Genre, subgenre, language, release year
- Precomputed audio features: danceability, energy, valence, tempo, acousticness, instrumentalness, speechiness, and liveness

#### 3.1.2 K-Nearest Neighbors Algorithm

KNN is a non-parametric, instance-based learning algorithm used to find the k most similar items to a given query item. Given a song $s_q$, the algorithm computes the distance between $s_q$ and all other songs in the catalog, then returns the $k$ songs with the smallest distance as candidates.

**Distance and Similarity Metrics.** The most commonly used metric is Cosine Similarity, which measures the angle between two feature vectors rather than their magnitude:

$$\text{cosine\_sim}(A, B) = \frac{A \cdot B}{\|A\| \cdot \|B\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \cdot \sqrt{\sum_{i=1}^{n} B_i^2}}$$

Alternatively, Euclidean Distance can be applied when the magnitude of feature values is meaningful:

$$d(A, B) = \sqrt{\sum_{i=1}^{n} (A_i - B_i)^2}$$

#### 3.1.3 Application in This System

Content-based KNN is primarily leveraged in the **Next-Song Recommendation** surface. Given the currently playing song, the system retrieves the $k$ most similar songs based on their feature vectors. This approach operates entirely on song metadata, requiring no user history — making it robust for scenarios where interaction data is sparse.

**Workflow:**
1. Construct a feature vector for each song from its metadata and audio attributes.
2. Normalize the feature vectors to ensure each dimension contributes equally.
3. For a query song $s_q$, compute similarity scores against all catalog songs.
4. Return the top-$k$ songs ranked by similarity as next-song candidates.

### 3.2 Collaborative Filtering (CF)

#### 3.2.1 Overview

Collaborative Filtering recommends items by exploiting patterns in user-item interactions. Unlike content-based methods, CF does not rely on item attributes — it infers preferences purely from the collective behavior of users. The underlying assumption is: *users who agreed in the past tend to agree in the future*.

The primary input to a CF system is a user-item interaction matrix $R$, where each entry $r_{ui}$ represents the interaction strength between user $u$ and item $i$. In this system, the interaction signal is the **playcount** field from the Kaggle dataset — an aggregated implicit feedback score used as a proxy for preference intensity. In the live serving pipeline, play duration collected from real user sessions plays the equivalent role.

$$R = \begin{pmatrix} r_{11} & r_{12} & \cdots & r_{1n} \\ r_{21} & r_{22} & \cdots & r_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ r_{m1} & r_{m2} & \cdots & r_{mn} \end{pmatrix}$$

where $m$ is the number of users and $n$ is the number of songs.

#### 3.2.2 Memory-Based Collaborative Filtering

Memory-based CF is a lazy learning approach that stores the entire interaction matrix and makes predictions at query time by directly computing similarities between users or items. It does not require a training phase and is straightforward to interpret.

There are two variants:
- **User-based CF**: Find users similar to the target user, then recommend songs those similar users have listened to.
- **Item-based CF**: Find songs similar to what the target user has interacted with, based on shared interaction patterns across users.

#### 3.2.3 Item-Based Collaborative Filtering

Item-based CF is the chosen approach in this system because it produces more stable similarity scores — item relationships change less frequently than user behavior — and scales more efficiently when the user base is large.

**Core Idea.** Two songs are considered similar if they have been listened to by the same group of users in the same way.

**Step 1 — Construct the item-item similarity matrix.** For each pair of songs $(i, j)$, compute their similarity based on the co-interaction vectors extracted from $R$. The Cosine Similarity between song vectors $\vec{s}_i$ and $\vec{s}_j$ (each of length $m$, representing interactions from all users) is:

$$\text{sim}(i, j) = \frac{\vec{s}_i \cdot \vec{s}_j}{\|\vec{s}_i\| \cdot \|\vec{s}_j\|}$$

**Step 2 — Generate candidates for a target user $u$.** Let $I_u$ be the set of songs user $u$ has interacted with. For each candidate song $c \notin I_u$, estimate the preference score as a weighted sum:

$$\hat{r}_{uc} = \frac{\sum_{i \in I_u} \text{sim}(c, i) \cdot r_{ui}}{\sum_{i \in I_u} |\text{sim}(c, i)|}$$

**Step 3 — Rank and return top-N recommendations.** Songs are sorted by $\hat{r}_{uc}$ in descending order and the top-N are returned as recommendations.

#### 3.2.4 Application in This System

Item-based CF is applied in the **Homepage Recommendation** surface to generate personalized candidate songs for each subscribed user. The system uses play duration as the implicit interaction signal $r_{ui}$, capturing listening depth as a proxy for user preference. Explicit signals (like/dislike) can further refine these scores as supplementary weights.

### 3.3 Relationship Between the Two Approaches

**Table 3: Comparison of Content-Based KNN and Item-Based CF**

| Dimension | Content-Based (KNN) | Item-Based CF |
|---|---|---|
| Data source | Song metadata & audio features | User-item interaction history |
| Similarity basis | Feature space proximity | Co-interaction patterns |
| Primary surface | Next-song recommendation | Homepage recommendation |
| Cold-start handling | Handles item cold-start well | Requires interaction history |
| Personalization level | Item-centric | User-behavior-driven |

Together, these approaches form a **hybrid candidate generation layer**: content-based KNN supplies song-to-song similarity candidates for continuous playback, while item-based CF supplies personalized candidates derived from the broader listening community's collective behavior.

### 3.4 Two-Tower Neural Retrieval Model

Beyond classical CF, the deployed system implements a **Two-Tower neural architecture** trained with a pairwise ranking objective (BPR). This model provides the primary retrieval stage for both recommendation surfaces in production.

#### 3.4.1 Architecture

The model consists of two independent deep encoder networks:

- **Item Tower**: encodes each song into a 64-dimensional L2-normalized embedding using song audio features and a one-hot genre vector. Architecture: `Linear(D_item → 128) → ReLU → Linear(128 → 64) → L2-normalize`.
- **User Tower**: encodes each user's listening profile into the same 64-dimensional space. The user representation is constructed as a play-ratio-weighted average of the audio feature vectors of songs the user has listened to, concatenated with a genre preference distribution and two activity statistics (average play ratio, normalized interaction count). Architecture: `Linear(D_user → 128) → ReLU → Linear(128 → 64) → L2-normalize`.

The compatibility score between a user embedding $\vec{u}$ and an item embedding $\vec{v}$ is the inner product (equivalently, cosine similarity after L2-normalization):

$$\text{score}(u, i) = \vec{u}^{\top} \vec{v}$$

#### 3.4.2 Item Feature Vector

For each song, the item feature vector is:

$$\vec{f}_{\text{item}} = [\text{audio features (10 dims)}, \text{genre one-hot (}|G|\text{ dims)}]$$

The 10 audio features are: popularity, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo — all normalized to approximately [0, 1].

#### 3.4.3 User Feature Vector

The user feature vector is constructed from listening history:

$$\vec{f}_{\text{user}} = \left[\underbrace{\frac{\sum_e w_e \cdot \vec{f}_{\text{audio}}(e)}{\sum_e w_e}}_{\text{weighted audio avg}}, \underbrace{\frac{\text{genre counts}}{\sum \text{genre counts}}}_{\text{genre preference}}, \underbrace{\bar{\rho},\ \min(N/100, 1)}_{\text{activity stats}}\right]$$

where $w_e = \max(\rho_e, 0.05)$ is the play ratio weight for event $e$, $\bar{\rho}$ is the mean play ratio, and $N$ is the total interaction count.

#### 3.4.4 Training Objective: Bayesian Personalized Ranking (BPR) Loss

##### Motivation: Pointwise vs. Pairwise vs. Listwise

Recommendation models can be optimized under three broad paradigms [6] (Zhang et al., 2023):

- **Pointwise**: treats each (user, item) interaction independently and trains a regressor or classifier to predict the absolute rating or probability of interaction. Matrix factorization and SVD fall into this category.
- **Pairwise**: considers a pair of items $(i^+, i^-)$ per user and optimizes the *relative ordering* — the model only needs to learn that the user prefers $i^+$ over $i^-$, not the absolute score. BPR belongs here.
- **Listwise**: directly optimizes a ranking metric (e.g., NDCG) over the full list of items. More powerful but significantly more expensive to compute.

Pairwise approaches are generally better suited to implicit-feedback scenarios such as music listening, where absolute engagement magnitudes are noisy but relative preferences are more reliable.

##### BPR: Bayesian Derivation

Bayesian Personalized Ranking (BPR) [3] is derived from the maximum a posteriori (MAP) estimator. Let $>_u$ denote the desired personalized total ordering of all items for user $u$, and $\Theta$ the model parameters. The posterior is:

$$p(\Theta \mid {>_u}) \propto p({>_u} \mid \Theta)\, p(\Theta)$$

Assuming pairwise independence across users and items, and that item $i$ is preferred over item $j$ by user $u$ with probability $\sigma(\hat{y}_{ui} - \hat{y}_{uj})$, the **BPR-OPT** criterion becomes:

$$\begin{aligned}
\text{BPR-OPT} &= \ln p(\Theta \mid {>_u}) \\
&\propto \sum_{(u,\, i,\, j)\,\in\, D} \ln \sigma(\hat{y}_{ui} - \hat{y}_{uj}) + \ln p(\Theta) \\
&= \sum_{(u,\, i,\, j)\,\in\, D} \ln \sigma(\hat{y}_{ui} - \hat{y}_{uj}) - \lambda_\Theta \|\Theta\|^2
\end{aligned}$$

where the training set is:

$$D \stackrel{\text{def}}{=} \{(u,i,j) \mid i \in I^+_u \wedge j \in I \setminus I^+_u\}$$

with $I^+_u$ the set of items user $u$ has positively interacted with, and $I \setminus I^+_u$ the remaining unobserved items. The Gaussian prior $p(\Theta) \propto \exp(-\lambda_\Theta \|\Theta\|^2)$ corresponds to L2 weight decay in the optimizer.

Maximizing BPR-OPT is equivalent to minimizing the following loss (negated, averaged over a batch):

$$\mathcal{L}_{\text{BPR}} = -\frac{1}{B} \sum_{(u,\, i^+,\, i^-)\,\in\, \mathcal{B}} \log \sigma\!\bigl(\hat{y}_{u i^+} - \hat{y}_{u i^-}\bigr)$$

which in the Two-Tower model corresponds to:

$$\hat{y}_{ui} = \text{score}(u, i) = \vec{u}^{\top} \vec{v}_i$$

and in PyTorch:

```python
loss = -F.logsigmoid(pos_scores - neg_scores).mean()
```

##### Sampling Strategy

**Positive items.** A track is treated as $i^+$ for user $u$ if its `playcount ≥ 2`, filtering out single accidental plays.

**Negative items.** To expose the model to hard, realistic negatives, negatives $i^-$ are drawn from a **popularity-biased distribution** (sampling probability $\propto \text{count}^{0.75}$), mixed with 20% uniform draws across the full catalog. Up to 30 re-sampling attempts are made per triplet to avoid accidentally selecting an item the user has interacted with. This mirrors the negative sampling strategy used in word2vec and has been shown to improve ranking quality over pure uniform sampling.

##### Hyperparameters

| Parameter | Value |
|---|---|
| Epochs | 10 |
| Steps per epoch | 120 |
| Batch size | 2,048 |
| Optimizer | Adam, lr = 1e-3, weight decay = 1e-6 |
| Negative mix (uniform %) | 20% |
| Positive threshold | playcount ≥ 2 |

### 3.5 XGBoost Re-Ranking Model

After the two-tower model generates a set of top-100 candidate songs via approximate nearest-neighbor search, an **XGBoost gradient-boosted tree** model re-ranks these candidates for the final top-N list.

The ranker is trained to predict the **play ratio** (proportion of a song's duration the user listened to) as a continuous relevance signal. For each (user, candidate song) pair, a joint feature vector is constructed:

| Feature | Description |
|---|---|
| `avg_play_ratio` | User's mean play ratio across all interactions |
| `total_plays_norm` | User's interaction count, normalized by 100 |
| `genre_match` | 1 if song genre matches user's top genre, else 0 |
| `popularity_norm` | Song popularity normalized to [0, 1] |
| Audio features (×10) | Raw audio feature values for the candidate song |
| `two_tower_score` | Retrieval score from the two-tower model |

Training uses squared error as the XGBoost objective, optimizing RMSE on the training split. The `two_tower_score` feature directly connects the retrieval stage to the ranking stage, allowing the ranker to calibrate the neural similarity score with observable engagement signals.

---

## 4 Dataset Description and Preprocessing Steps

### 4.1 Music Information Dataset

The Music Information dataset serves as the item catalog for the content-based filtering component of the recommendation system. It contains **1,500 song records**, each uniquely identified by a `track_id` derived from the MusicBrainz database, with no duplicate entries across the catalog. The dataset spans 58 distinct release years ranging from 1933 to 2019, providing a broad historical coverage of recorded music across multiple decades and genres.

Each record contains 18 fields organized into three distinct categories:
1. **Track identifiers and metadata**: `track_id`, `name`, `artist`, `year`, `spotify_id`, `spotify_preview_url`, `tags`.
2. **Categorical genre label**: each song is assigned to exactly one of 15 genres — Rock, Electronic, Metal, Jazz, Country, Rap, Reggae, Blues, Pop, RnB, Punk, Folk, Latin, New Age, and World — with a perfectly balanced distribution of **100 songs per genre**.
3. **Nine numerical audio feature attributes** computed by the Spotify audio analysis engine: danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, and tempo.

The audio features exhibit wide value ranges: danceability from 0.060 to 0.980, energy from 0.000 to 0.999, tempo from 36.849 to 219.993 BPM, loudness from −32.779 to −0.590 dB. The `tags` field contains 81 null entries (≈5.4%); all other columns are fully populated.

> **Note on feature dimensionality.** The Two-Tower model uses **10** audio-derived input features rather than 9. The additional feature, `popularity` (a 0–100 integer from the Spotify catalog, stored in the track metadata section), is normalized to [0, 1] and prepended to the 9 Spotify audio attributes to form a unified 10-dimensional audio vector. The classical KNN pipeline (Section 4.3 Step 3) operates on the original 9 attributes only, as popularity is not an intrinsic audio property.

### 4.2 User Listening History Dataset

The User Listening History dataset captures the interaction signals between users and tracks. It contains **45,891 interaction records** linking **30,089 unique users** to **895 unique tracks**. Every `track_id` in this dataset has a matching entry in the Music Information catalog, establishing complete referential integrity. All six columns are fully populated.

> **Scope note.** This section describes the subset of the Kaggle listening-history source that was loaded into the live system for demonstration purposes. The offline model evaluation in Section 7 was conducted on the full, unfiltered Kaggle source, which contains more users, tracks, and interactions; see Section 7.1 for the exact evaluation-dataset statistics.

Each record contains:
- `track_id`, `user_id` (SHA-1 hashed for anonymity)
- `playcount`: raw aggregated play count from the Kaggle dataset, ranging from 1.01 to 499.99 (mean ≈ 249.21). The non-integer values reflect the Kaggle source's aggregation methodology; the field is used as a continuous implicit feedback signal throughout this system.
- `is_like`, `is_dislike`: binary explicit feedback (49.7% like, 25.4% dislike)
- `score`: composite engagement metric ranging from −0.598 to 100.798 (mean ≈ 50.04)

### 4.3 Preprocessing Steps

#### Step 1: Character Encoding Correction
Both CSV files are loaded using Latin-1 (ISO 8859-1) encoding to correctly handle accented characters in non-English artist names and tags.

#### Step 2: Missing Value Handling
The 81 null entries in the `tags` field are filled with an empty string. No numerical imputation is required; all audio features and interaction columns are complete.

#### Step 3: Feature Selection for Content-Based Filtering
The KNN feature vector is constructed exclusively from the nine Spotify audio attributes. Metadata fields and unstructured text are excluded. Genre and year are retained as categorical filters during candidate retrieval.

#### Step 4: Feature Normalization
All nine audio features are rescaled to the [0, 1] range using min-max normalization to prevent high-magnitude features (e.g., tempo: 36–220 BPM; loudness: −32.8 to −0.6 dB) from dominating cosine similarity calculations.

#### Step 5: Referential Integrity Verification
All 895 tracks in the listening history are confirmed to have matching entries in the music catalog. Tracks with no interaction history are retained for content-based fallback but excluded from the collaborative filtering model.

#### Step 6: User-Item Matrix Construction
The interaction data is pivoted into a user-item matrix of dimensions 30,089 × 895. The matrix density is approximately **0.17%** (sparsity 99.83%). Unobserved cells are treated as missing (not zero).

#### Step 7: Per-User Score Normalization
Scores within the user-item matrix are normalized on a per-user basis using min-max scaling to the [0, 1] interval, ensuring that less active users contribute equally informative preference signals.

#### Step 8: Train-Test Splitting
For each user with at least two distinct interactions, a held-out subset of interactions is designated as the test set. Users with fewer than two interactions are excluded from evaluation but remain eligible for content-based fallback recommendations.

---

## 5 System Design

### 5.1 Architectural Overview

The recommendation system is organized around two distinct recommendation surfaces, each served by a layered ML pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    Recommendation Surfaces                   │
│                                                             │
│  ┌────────────────────┐    ┌────────────────────────────┐   │
│  │  Homepage Surface  │    │   Next-Song Surface        │   │
│  │  (Personalized)    │    │   (Content-Based KNN)      │   │
│  └────────┬───────────┘    └──────────┬─────────────────┘   │
└───────────┼──────────────────────────┼─────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────────────────────────────────────────┐
│         Candidate Generation Layer  ◄── PRIMARY FOCUS     │
│                                                           │
│  [Homepage]  User Tower ──► User Embedding                │
│              Item Embeddings pre-indexed in pgvector      │
│              ANN Search (cosine distance) → Top-100       │
│                                                           │
│  [Next-Song] KNN on normalized audio feature vectors      │
│              Cosine similarity over catalog → Top-100     │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│          Re-Ranking Layer  (placeholder — future work)    │
│                                                           │
│  XGBoost Ranker  [not fully implemented in this phase]    │
│  Input: [user stats, song audio, genre match,             │
│           two_tower_score]                                │
│  Output: Predicted play ratio → ranked top-N              │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│              Response with TTL Caching (5 min)            │
└───────────────────────────────────────────────────────────┘
```

> **Scope note.** In this assignment the primary contribution is the **candidate generation** stage — training the Two-Tower retrieval model and evaluating the quality of the candidate set it produces. The XGBoost re-ranking layer is included in the codebase as a structural placeholder to illustrate the intended full pipeline, but its training and evaluation are out of scope for this phase.

### 5.2 Homepage Recommendation (Personalized)

The homepage surface delivers personalized song lists for subscribed users. The end-to-end flow is:

1. **User Profile Encoding**: the user's listening history (play events, durations) is aggregated into a feature vector and encoded by the User Tower into a 64-dimensional embedding.
2. **ANN Retrieval**: the user embedding is used as a query vector against the pgvector index over all song embeddings, returning the top-100 nearest neighbors by cosine distance. This candidate retrieval step is the core deliverable of this phase.
3. **Re-Ranking** *(placeholder)*: an XGBoost ranker is provisioned in the codebase to re-score the 100 candidates, but is not fully trained or evaluated in this assignment. Candidates are currently ordered by the two-tower retrieval score directly.
4. **Top-10 Delivery**: the top 10 candidates are returned and cached with a 5-minute TTL.

If the ML runtime is unavailable (models not loaded), the system falls back to a deterministic hash-based sort over all songs.

### 5.3 Next-Song Recommendation

The next-song surface recommends similar follow-up tracks given the currently playing song. This surface is driven purely by **content-based KNN** on normalized song audio features — consistent with Section 3.1.3. The flow is:

1. **Feature Lookup**: the currently playing song's pre-computed, min-max-normalized audio feature vector (9 attributes) is retrieved from the song catalog.
2. **KNN Retrieval**: cosine similarity is computed between the query song's feature vector and every other song in the catalog. The top-100 most similar songs (excluding the current song) are returned as candidates.
3. **Re-Ranking** *(placeholder)*: the XGBoost ranker is applied structurally but is not fully implemented in this phase; candidates are currently ordered by cosine similarity score.
4. **Top-6 Delivery**: the top 6 candidates are returned and cached.

This surface requires no user history — it relies solely on song-to-song audio similarity, making it robust for new users and cold-start scenarios.

### 5.4 Feature Engineering

The feature engineering layer transforms raw song metadata and user interaction logs into the dense vector representations consumed by the neural towers and the tree-based ranker.

**Item features** (dimension = 10 audio + |G| genres):

| Component | Features |
|---|---|
| Audio (normalized) | popularity/100, danceability, energy, loudness-scaled, speechiness, acousticness, instrumentalness, liveness, valence, tempo/200 |
| Genre | One-hot vector over genre vocabulary |

**User features** (dimension = 10 audio + |G| genres + 2 activity stats):

| Component | Features |
|---|---|
| Weighted audio average | Play-ratio-weighted mean of listened songs' audio vectors |
| Genre preference | Normalized genre interaction counts |
| Activity statistics | Mean play ratio, normalized total interaction count |

**Ranking features** (dimension = 14):

| Feature | Description |
|---|---|
| avg_play_ratio | User's mean play completion rate |
| total_plays_norm | Normalized interaction count |
| genre_match | Binary: song genre matches user's top genre |
| popularity_norm | Song popularity / 100 |
| Audio features (×10) | Raw (un-normalized) audio features |
| two_tower_score | Cosine similarity from ANN retrieval |

### 5.5 Vector Index and Approximate Nearest Neighbor Search

Song item embeddings (64-dimensional, L2-normalized) are stored in a PostgreSQL `pgvector` column on the `songs` table. At query time, the `<=>` cosine distance operator performs approximate nearest-neighbor search, returning the top-100 closest songs in sub-linear time. This design eliminates the need for a separate vector database and enables atomic consistency between the song catalog and its embeddings.

To inform the choice of ANN backend, five retrieval methods were benchmarked on the same 64-dimensional embedding space across 200 queries. The methods evaluated span the full spectrum from exact brute-force to approximate indexing:

- **NumPy exact brute force**: baseline; computes pairwise cosine similarity over the full catalog on every query.
- **FAISS Flat exact**: GPU-accelerated exact search using Facebook AI Similarity Search.
- **FAISS IVF approximate**: inverted file index that partitions the space into Voronoi cells, probing only a subset per query.
- **HNSW approximate**: Hierarchical Navigable Small World graph-based index with high recall.
- **Annoy approximate**: tree-based approximate index by Spotify.

The results of this benchmark are reported in Section 7.5.

### 5.6 Model Registry and Serving

All trained models are versioned and stored in **MLflow Model Registry** under three registered model names:

| Model | Type | Purpose |
|---|---|---|
| `music-item-tower` | PyTorch | Encodes song features → 64-d item embedding |
| `music-user-tower` | PyTorch | Encodes user history → 64-d user embedding |
| `music-ranker` | XGBoost | Re-ranks candidates by predicted play ratio *(placeholder — not fully implemented in this phase)* |

At server startup, the `MLRuntime` class loads the latest "Production" version of each model from MLflow. If any model is unavailable, the system degrades gracefully to the deterministic fallback.

---

## 6 AI Pipeline for Data Training and Deployment

### 6.1 Pipeline Overview

The AI pipeline follows a standard **offline training → online serving** pattern, with MLflow as the experiment tracking and model registry backbone.

```
Data Collection         Training                    Deployment
──────────────          ────────                    ──────────
User Events       ─►   Two-Tower Train        ─►   MLflow Registry
Song Catalog      ─►   (BPR loss)                   (item-tower,
                        ← PRIMARY FOCUS →           user-tower)
                                                         │
                  ─►   XGBoost Train          ─►   MLflow Registry
                        (play-ratio label)          (ranker)
                        [placeholder —              [placeholder]
                         out of scope]                   │
                                                         ▼
                                                  Online Serving
                                                  (MLRuntime loads
                                                   at startup)
```

### 6.2 Data Collection

Training data is sourced from two streams:

1. **Song catalog**: static item features from the Music Information dataset (audio features, genre, metadata), loaded into the `songs` table.
2. **Analytics events**: dynamic user interaction logs (`AnalyticsEvent` records) capturing `play_duration_seconds`, `song_duration_seconds`, `user_id`, `song_id`, and explicit feedback (`is_like`, `is_dislike`).

### 6.3 Two-Tower Model Training

**Input preparation:**
- BPR triplets $(u, i^+, i^-)$ are sampled at training time. A track qualifies as a positive item if the user's `playcount ≥ 2`.
- Users without any qualifying positive item are excluded from training (2 out of 803 users in the experiment).
- Negative items are drawn from a popularity-weighted distribution (popularity$^{0.75}$) mixed with 20% uniform draws, with up to 30 re-sampling attempts per triplet to avoid accidentally sampling a seen item.

**Training procedure:**
- Framework: PyTorch, Adam optimizer, learning rate 1e-3, weight decay 1e-6
- Epochs: 10 | Steps per epoch: 120 | Batch size: 2,048
- Loss: BPR — `loss = -F.logsigmoid(pos_scores - neg_scores).mean()`
- The final BPR loss is logged to MLflow.

**Model registration:**
- Both `ItemTower` and `UserTower` are logged as separate PyTorch models in MLflow.
- The latest versions are automatically transitioned to the "Production" alias.
- Feature artifacts (genre vocabulary, input dimensions) are stored as a JSON artifact alongside the models.

### 6.4 XGBoost Ranking Model Training

**Input preparation:**
- Training examples are constructed from all analytics events with a non-zero play ratio.
- The label is the continuous play ratio $\rho \in [0, 1]$ for each (user, song) interaction.
- Each example is encoded as a 14-dimensional ranking feature vector.
- If fewer than 16 real examples exist, synthetic examples are generated using genre similarity heuristics.

**Training procedure:**
- Library: XGBoost, objective: `reg:squarederror`
- Training RMSE is logged to MLflow.

**Model registration:**
- The trained booster is logged and registered in MLflow under `music-ranker`.
- The latest version is transitioned to "Production."

### 6.5 Offline Evaluation Workflow

Before deploying a new model version, the following offline evaluation protocol is applied (corresponding to the experimental notebook):

1. **Train/test split** at the user level (80/20 split), ensuring every evaluated user has training history.
2. **Rating prediction evaluation**: for a random sample of 2,000 test interactions, RMSE and MAE are computed between predicted and actual playcount values.
3. **Ranking evaluation**: for each of up to 25 test users, unseen candidates are ranked by predicted score. Precision@K, Recall@K, and NDCG@K are computed at K ∈ {5, 10, 20} using a relevance threshold of playcount ≥ 1.

### 6.6 Online Serving and Caching

At request time, the `MLRuntime` singleton:
1. Loads models from MLflow on startup (synchronous, blocking).
2. Executes the two-tower retrieval and XGBoost re-ranking in-process.
3. Caches results in a TTL-based in-memory store (5-minute expiry).
4. Invalidates the cache on user feedback events (likes/dislikes) to refresh personalization.

---

## 7 Evaluation Results

### 7.1 Experimental Setup

**Dataset:** The experiments are conducted on the **full Kaggle listening-history source** (before the system-specific subsetting described in Section 4.2), filtered to users with at least 150 interactions and tracks with at least 1,000 users — yielding 803 active users, 2,172 tracks, and 74,853 ratings. The user-item matrix density after filtering is 3.46%.

**Train/test split:** 80% training (59,882 records), 20% test (14,971 records), random split with seed 42.

**Models evaluated:**
1. **User-Based CF (UBCF)**: cosine similarity on mean-centered user vectors; top-20 similar users for prediction.
2. **Item-Based CF (IBCF)**: cosine similarity on mean-centered item vectors; top-20 similar items for prediction.
3. **SVD**: Truncated SVD with 50 latent factors, matrix factorization baseline.
4. **Two-Tower BPR**: hybrid two-tower network with BPR loss, genre one-hot item features, and user activity auxiliary statistics; trained for 10 epochs with batch size 2,048.

**Evaluation metrics:**
- **RMSE** and **MAE**: rating prediction accuracy on a held-out sample of 2,000 test interactions (playcount scale).
- **Precision@K**, **Recall@K**, **NDCG@K** at K ∈ {5, 10, 20}: ranking quality using relevance threshold of playcount ≥ 1, evaluated over 25 test users with up to 400 candidate items per user.

### 7.2 Rating Prediction Results

**Table 4: Rating Prediction — RMSE and MAE**

| Model | RMSE | MAE | Coverage |
|---|---|---|---|
| User-Based CF | 2.8491 | 1.2910 | 99.9% |
| Item-Based CF | **2.7658** | **1.1479** | 99.9% |
| SVD | 2.8166 | 1.2701 | 99.9% |
| Two-Tower BPR | 3.2419 | 2.2100 | 99.9% |

Item-Based CF achieves the best RMSE (2.7658) and MAE (1.1479), indicating it most accurately predicts the magnitude of a user's playcount for a given track. The Two-Tower BPR model scores highest on RMSE and MAE; however, this is expected because BPR is a **ranking** model — it is trained with a pairwise ranking objective rather than a pointwise prediction objective. Rating prediction accuracy is therefore not a meaningful measure of its quality.

### 7.3 Ranking Quality Results

**Table 5: Ranking Metrics — Precision, Recall, and NDCG @ K**

| Model | P@5 | R@5 | NDCG@5 | P@10 | R@10 | NDCG@10 | P@20 | R@20 | NDCG@20 |
|---|---|---|---|---|---|---|---|---|---|
| User-Based CF | 0.0080 | 0.0014 | 0.0200 | 0.0080 | 0.0034 | 0.0342 | 0.0140 | 0.0122 | 0.0748 |
| Item-Based CF | 0.0080 | 0.0020 | 0.0172 | 0.0120 | 0.0066 | 0.0430 | 0.0220 | 0.0189 | 0.0927 |
| SVD | 0.0640 | 0.0123 | 0.1453 | 0.0400 | 0.0171 | 0.1601 | 0.0240 | 0.0252 | 0.1601 |
| **Two-Tower BPR** | **0.0880** | **0.0225** | **0.2211** | **0.0600** | **0.0290** | **0.2341** | **0.0440** | **0.0422** | **0.2651** |

The Two-Tower BPR model dominates all ranking metrics at every K value:
- **NDCG@5 = 0.2211** vs. SVD's 0.1453 — a **52% relative improvement** in top-5 ranking quality.
- **NDCG@20 = 0.2651** vs. SVD's 0.1601 — a **66% relative improvement** at K=20.
- Precision@5 = 0.0880 vs. memory-based CF at 0.008 — an **11× improvement**.

SVD outperforms both memory-based methods significantly, demonstrating the value of latent factor decomposition. However, the neural Two-Tower model with BPR outperforms SVD by a substantial margin across all ranking metrics, reflecting its ability to learn more expressive item and user representations.

### 7.4 Training Convergence (Two-Tower BPR)

The Two-Tower BPR model trains stably with monotonically decreasing BPR loss:

| Epoch | Loss |
|---|---|
| 1 | 0.6319 |
| 2 | 0.5718 |
| 3 | 0.5593 |
| 5 | 0.5466 |
| 8 | 0.5404 |
| 10 | 0.5380 |

The loss curve shows rapid initial convergence (epochs 1–3) followed by gradual refinement, with no signs of divergence or instability.

### 7.5 ANN Retrieval Benchmark

To validate the candidate generation layer independently of model quality, five ANN methods were benchmarked across 200 queries against a 64-dimensional embedding catalog. Recall@K is defined as the fraction of true top-K exact neighbors recovered by the approximate method.

**Table 6: ANN Retrieval Benchmark Results**

| Method | Build (s) | Query total (s) | Avg ms/query | Recall@K |
|---|---|---|---|---|
| NumPy exact brute force | 0.0000 | 0.0610 | 0.305 | **1.0000** |
| FAISS Flat exact | 0.0046 | 0.1310 | 0.655 | **1.0000** |
| FAISS IVF approximate | 0.1591 | 0.0172 | **0.086** | 0.9555 |
| HNSW approximate | 2.4231 | 0.0683 | 0.341 | 0.9980 |
| Annoy approximate | 0.7530 | 0.1870 | 0.935 | 0.8895 |

**Key observations:**

- **FAISS IVF** achieves the lowest per-query latency (0.086 ms/query), a **7.5× speedup** over brute force, at a modest recall cost (95.6%). It is the best choice when throughput is the priority.
- **HNSW** delivers near-exact recall (99.8%) with a competitive query time (0.341 ms/query), making it the best trade-off between accuracy and speed. It requires more index build time (2.4 s) but this is a one-time offline cost.
- **Annoy** has the highest query latency among approximate methods and the lowest recall (88.9%), making it the least suitable option for this use case.
- **FAISS Flat** is exact but slightly slower than brute force per query due to framework overhead at this catalog size; its advantage emerges at larger scales.

**Choice for production.** The system uses pgvector's built-in IVFFlat-style index (via the `<=>` operator), which offers a recall and latency profile comparable to FAISS IVF — acceptable recall loss in exchange for sub-millisecond retrieval — without requiring a separate vector store. At the current catalog size (1,500 songs), even exact search is fast enough; the ANN index becomes critical as the catalog scales to millions of tracks.

### 7.6 Discussion

**Rating prediction vs. ranking.** The evaluation results reveal a fundamental tension between rating prediction accuracy and ranking quality. Item-Based CF achieves the lowest RMSE and MAE, yet its ranking metrics (NDCG@5 = 0.0172) are among the worst. Conversely, the Two-Tower BPR model has the highest RMSE but delivers the best ranking performance. This confirms that RMSE/MAE are insufficient metrics for recommendation quality — ranking-oriented metrics (NDCG, Precision@K) better reflect the practical utility of a recommendation system.

**Memory-based methods.** User-Based and Item-Based CF produce very similar ranking performance, both substantially below SVD and Two-Tower BPR. This reflects the well-known limitations of memory-based methods under high sparsity (3.46% matrix density): similarity estimates become noisy, and the signal-to-noise ratio in the neighbor set is low.

**SVD as a strong baseline.** SVD captures global latent structure in the interaction matrix and produces NDCG@5 = 0.1453, a significant improvement over memory-based methods. This validates matrix factorization as a practical baseline for music recommendation.

**Two-Tower BPR.** The neural two-tower model with BPR training and popularity-biased negative sampling achieves the best ranking across all K values. The item tower's combined use of normalized audio features and a genre one-hot vector, together with the user tower's activity auxiliary statistics, provides richer representations than the interaction-only signals available to memory-based and SVD methods — particularly beneficial in the music domain where genre is a strong predictor of preference.

**Implications for deployment.** Based on these results, the production system correctly prioritizes the Two-Tower model for candidate retrieval (ranking-quality-critical) and delegates the final ordering to the XGBoost re-ranker, which can further personalize using user engagement statistics not available at training time. Memory-based CF serves as a conceptual and experimental baseline rather than a production component.

---

## References

[1] Xavier Amatriain, Justin Basilico, and Jisoo Joo. Recommender systems in industry: A Netflix case study. In *Recommender Systems Handbook*, chapter 8.1: Beyond explicit ratings. 2015. https://amatria.in/pubs/Recsys-in-industry.pdf.

[2] Dinesh Asanka. Into thin air to touching the void. https://dbfriend.blogspot.com/2021/02/into-thin-air-to-touching-void.html. Data is everywhere, but?, 27/02/2021.

[3] Steffen Rendle, Christoph Freudenthaler, Zeno Gantner, and Lars Schmidt-Thieme. BPR: Bayesian Personalized Ranking from Implicit Feedback. In *Proceedings of the 25th Conference on Uncertainty in Artificial Intelligence (UAI)*, 2009.

[4] Yann LeCun, Yoshua Bengio, and Geoffrey Hinton. Deep learning. *Nature*, 521(7553):436–444, 2015.

[5] Aaron van den Oord, Yazhe Li, and Oriol Vinyals. Representation Learning with Contrastive Predictive Coding. *arXiv preprint arXiv:1807.03748*, 2018.

[6] Aston Zhang, Zachary C. Lipton, Mu Li, and Alexander J. Smola. *Dive into Deep Learning*, Section 21.5: Personalized Ranking for Recommender Systems. 2023. https://d2l.ai/chapter_recommender-systems/ranking.html

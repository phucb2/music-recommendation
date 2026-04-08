# PRD: Music Recommendation System for Subscribed Users

## 1. Objective

Build a scalable music recommendation system for **subscribed users** that improves music discovery and listening engagement on two product surfaces:

1. **Homepage recommendation**
2. **Next-song recommendation**

The system should use simple, practical ML methods in the first version and rely on user interaction data plus song metadata.

---

## 2. Background

The company is a subscription-based music streaming platform that helps users discover and play music online.

Today, the platform has:

* core playback and catalog browsing,
* limited personalization,
* limited analytics and tracking.

Because of this, users may not receive relevant music recommendations on the homepage, and playback may end early when the next suggested song is not a good fit.

This reduces:

* music discovery quality,
* user engagement,
* and long-term subscription value.

The recommendation system will be introduced as a new personalization layer in the existing product.

---

## 3. Problem Statement

Subscribed users need better personalized recommendations so they can:

* discover music that matches their taste,
* continue listening without interruption,
* and get more value from the platform.

The business needs a recommendation system that:

* increases meaningful listening from recommendation surfaces,
* avoids optimizing for shallow clicks,
* and is simple enough to deploy and scale in an early version.

---

## 4. Users

### In scope

* subscribed users with listening history

### Out of scope

* non-subscribed users
* cold-start users with no history
* cold-start songs
* free-tier recommendation use cases

---

## 5. Product Scope

## 5.1 In scope

### A. Homepage recommendation

Recommend songs on the homepage to help users discover music tailored to their preferences.

### B. Next-song recommendation

Recommend the next song while the user is listening.

### C. Data and modeling scope

* use song metadata only
* use play duration as the main implicit signal
* use like / dislike as explicit feedback
* use scalable candidate generation and recommendation modeling

---

## 5.2 Out of scope

* raw song audio, lyrics, or deep content models
* playlist generation
* session-aware next-song modeling
* contextual bandits / exploration optimization
* advanced ranking stack
* heavy feature-store architecture

For **next-song recommendation**, only **song-to-song similarity** is in scope.
**Session context is out of scope** for this version.

---

## 6. Where the New ML System Fits

The recommendation system is a **new personalization layer** inside the existing streaming platform.

It sits between:

* the existing **product surfaces**
  (homepage, player, autoplay / queue),
* and the existing **platform systems**
  (catalog, playback, subscription/account services).

### Existing systems

* subscription/account service
* music catalog service
* playback service
* frontend app / website

### New ML components

* event tracking
* simple feature generation
* candidate generation
* recommendation model service
* recommendation API

### High-level flow

1. collect user interaction data,
2. build simple user and song representations,
3. generate song candidates,
4. score/order them,
5. return recommendations to homepage or player.

---

## 7. Requirements

## 7.1 Functional requirements

### Homepage recommendation

The system must:

* generate personalized song candidates for each subscribed user,
* rank/order candidate songs for homepage display,
* support discovery beyond the user’s exact listening history,
* avoid excessive repetition.

### Next-song recommendation

The system must:

* suggest a next song based on **song-to-song similarity**,
* personalize results when possible using historical user preference,
* return results with low enough latency to support continuous playback.

---

## 7.2 Non-functional requirements

* recommendation serving must be scalable to large user and catalog sizes
* online recommendation latency must be acceptable for interactive use
* next-song latency must be lower than homepage latency
* the system must support periodic model refresh
* the system must support logging for training and evaluation

---

## 8. Data Requirements

## 8.1 Explicit feedback

Use:

* like / favorite
* dislike / hide

These are strong but sparse signals.

## 8.2 Implicit feedback

Use:

* **play duration**

This is the main behavioral signal for the first version.

Examples of derived interpretation:

* long play duration = positive preference
* very short play duration = negative preference
* medium play duration = weak positive or neutral

---

## 8.3 Interaction data to log

At minimum:

* `user_id`
* `song_id`
* `timestamp`
* `surface`
* `event_type`
* `play_duration_seconds`
* `song_duration_seconds`
* `session_id`

---

## 8.4 Song metadata required

The recommendation system should use metadata such as:

* `song_id`
* `artist_id`
* `album_id`
* `genre`
* `subgenre`
* `language`
* `release_date` or `release_year`
* `duration_seconds`
* `singer`
* `composer / author`
* `featured_artists`
* `country / region`
* `explicit_content_flag`
* `historical popularity`

These fields support both similarity-based retrieval and collaborative models.

---

## 9. Recommendation Approach

## 9.1 Homepage recommendation

### ML framing

Homepage recommendation is a **personalized ranking of candidate songs for each user**.

For each subscribed user:

1. generate a candidate pool,
2. estimate relevance using user behavior and song information,
3. return an ordered list of songs.

### Candidate generation sources

Homepage candidates can come from:

#### A. Collaborative filtering candidates

Use user-song interaction patterns based on play duration.

Example:

* users with similar long-listen behavior also listened to these songs

#### B. Metadata-similar candidates

Retrieve songs similar to songs the user already likes using:

* artist
* genre
* language
* singer
* release era

#### C. Preference-based expansion

Use the user’s top artists, genres, and languages to retrieve additional songs.

#### D. Popularity fallback

Use popular songs filtered by broad user taste.

### Candidate merge

Merge candidates from the above sources, deduplicate them, then pass them to the homepage recommendation model.

---

## 9.2 Next-song recommendation

### ML framing

Next-song recommendation is a **song-to-song similarity task**.

It should recommend songs similar to the currently playing song.

### In-scope logic

Use:

* same artist
* related artists
* same genre / subgenre
* same language
* similar release era
* similar metadata tags if available

### Out of scope

Do not use:

* session-aware ranking
* session sequence modeling

### Personalization

A light personalization layer may be applied using user history, for example:

* prefer artists or genres the user tends to listen to longer,
* downweight songs from categories the user often abandons quickly.

But the core next-song logic remains **song-song similarity**.

---

## 10. Model Requirements

## 10.1 Core recommendation model

The main recommendation logic should focus on **collaborative filtering**, with a **two-tower model** as the preferred scalable implementation.

### Option A: Classical collaborative filtering

Use user-song interaction data derived from play duration to learn latent embeddings for:

* users
* songs

This can be implemented with matrix factorization or implicit-feedback collaborative filtering.

### Option B: Two-tower model

This is the preferred scalable design.

#### User tower

Build a user embedding using:

* historical listening behavior
* top artists
* top genres
* preferred language
* recency-weighted play duration behavior

#### Song tower

Build a song embedding using:

* artist
* genre
* language
* singer
* release era
* popularity

#### Training objective

Train the model so that:

* songs with strong positive listening signals are closer to the user,
* irrelevant songs are farther away.

This supports efficient retrieval using nearest-neighbor search.

---

## 10.2 Why this model fits

This approach is suitable because it:

* works well with play-duration-based implicit feedback,
* scales well for large catalogs,
* supports retrieval efficiently,
* combines interaction data and metadata,
* keeps the first version practical.

---

## 11. Success Metrics

## 11.1 North-star metric

### Qualified listening from recommendations

**Definition:**
Total listening time generated from recommendation surfaces per active subscribed user, where a recommended play must pass a minimum quality threshold.

### Why this metric

This is the primary metric because it:

* reflects actual listening consumption,
* avoids optimizing for clickbait,
* aligns better with user value than clicks alone.

### Example qualification rule

A play counts as qualified if:

* play duration >= 30 seconds, or
* play duration >= 50% of song duration

### Example formula

[
\text{Qualified Listening from Recommendations} =
\frac{\sum \text{qualified play duration from recommendation surfaces}}{\text{active subscribed users}}
]

Recommendation surfaces:

* homepage recommendations
* next-song recommendations

---

## 11.2 Supporting online metrics

### Homepage CTR

[
\text{Homepage CTR} =
\frac{\text{homepage recommendation clicks}}{\text{homepage recommendation impressions}}
]

Where:

* impression = a song recommendation is shown on homepage
* click = user clicks/taps the recommendation

---

### Skip rate

[
\text{Skip Rate} =
\frac{\text{recommended songs skipped before threshold}}{\text{recommended songs played}}
]

A skip can be defined as:

* playback stopped within first 30 seconds, or
* playback duration < 20% of song duration

This should be reported separately for:

* homepage recommendations
* next-song recommendations

Lower skip rate indicates better relevance.

---

## 11.3 Offline metrics

### Recall@K

[
\text{Recall@K} =
\frac{\text{relevant items retrieved in top K}}{\text{number of relevant items}}
]

Use this to evaluate retrieval quality.

### NDCG@K

Use this to evaluate ranking quality, especially where top positions matter.

---

## 12. Feedback Loop

The recommendation system should improve through a simple feedback loop:

1. recommend songs,
2. collect user interactions,
3. log play duration and explicit feedback,
4. convert interaction data into training signals,
5. retrain or refresh the model,
6. serve updated recommendations.

Because analytics are currently limited, logging and data collection are part of the MVP.

---

## 13. Latency Requirement

Keep latency requirements simple.

* homepage recommendation should return within acceptable interactive latency
* next-song recommendation should be faster than homepage recommendation because it affects playback continuity

A practical approach:

* precompute or cache parts of user/song representations
* use efficient nearest-neighbor retrieval
* avoid full-catalog online scoring

---

## 14. MVP Summary

The MVP should deliver:

* homepage recommendation for subscribed users
* next-song recommendation based on song-song similarity
* collaborative filtering / two-tower recommendation modeling
* play-duration-based learning
* basic explicit feedback support
* candidate generation from collaborative, metadata, and popularity sources
* online logging and offline evaluation

This keeps the first version focused, scalable, and aligned with the business goal of increasing meaningful listening from recommendations.

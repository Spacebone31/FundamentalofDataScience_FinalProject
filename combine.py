import pandas as pd

# Load both CSV files
social_media_metrics = pd.read_csv("igunique (1).csv")
audio_features = pd.read_csv("spotify_audio_features_with_metadata.csv")

# Normalize case to ensure matches
social_media_metrics['username'] = social_media_metrics['username'].str.lower()
audio_features['username'] = audio_features['username'].str.lower()

# Merge data from both CSVs based on the 'username' column
# We'll use an outer join to retain all data, and then fill missing values if needed
merged_data = pd.merge(
    audio_features,
    social_media_metrics,
    on='username',
    how='left'  # Keep all rows from audio_features, add columns from social_media_metrics if usernames match
)

# Save the updated data to the original or a new CSV
merged_data.to_csv("final_data.csv", index=False)

print("Data has been successfully merged and saved.")

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def merge_and_predict_missing_users(aidev_path, github_path, output_path):
    print("Loading datasets...")
    aidev_df = pd.read_csv(aidev_path)
    github_df = pd.read_csv(github_path)

    aidev_df['login'] = aidev_df['login'].astype(str).str.strip()
    github_df['login'] = github_df['login'].astype(str).str.strip()

    target_cols = [
        'collab_breadth', 
        '5yr_public_commits', 
        '5yr_private_work', 
        '5yr_reviews_given', 
        '5yr_prs_opened'
    ]
    feature_cols = [col for col in aidev_df.columns if col != 'login']

    train_df = pd.merge(aidev_df, github_df, on='login', how='inner')
    missing_df = aidev_df[~aidev_df['login'].isin(github_df['login'])].copy()

    print(f"Total users in AIdev file: {len(aidev_df)}")
    print(f"Users found in both files (Training Set size): {len(train_df)}")
    print(f"Users missing GitHub data (Prediction Set size): {len(missing_df)}")

    if len(train_df) == 0:
        raise ValueError("Error: No overlapping users found between both CSV files to train on.")

    X_train = train_df[feature_cols]
    y_train = train_df[target_cols]

    print("Training RandomForestRegressor model...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    if not missing_df.empty:
        print("Predicting missing values...")
        X_missing = missing_df[feature_cols]
        predictions = rf_model.predict(X_missing)
        
        pred_df = pd.DataFrame(predictions, columns=target_cols, index=missing_df.index)
        
        for col in target_cols:
            missing_df[col] = pred_df[col].round().astype(int)
        
        final_df = pd.concat([train_df, missing_df], ignore_index=True)
    else:
        print("No missing users detected. All data already combined via inner join.")
        final_df = train_df

    for col in target_cols:
        final_df[col] = final_df[col].round().astype(int)

    final_df.to_csv(output_path, index=False)
    print(f"Process complete! Output successfully saved with integer predictions to '{output_path}'.")

if __name__ == "__main__":
    AIDEV_FILE = '../../data/prepare_data/data_from_aidev.csv'
    GITHUB_FILE = '../../data/prepare_data/data_from_github.csv'
    OUTPUT_FILE = '../../data/prepare_data/final_combined_data_tmp.csv'
    
    merge_and_predict_missing_users(AIDEV_FILE, GITHUB_FILE, OUTPUT_FILE)
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def merge_and_predict_missing_users(aidev_path, github_path, output_path, eval_path):
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

    eval_train_df, eval_test_df = train_test_split(
        train_df, test_size=0.2, random_state=42
    )

    eval_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    eval_model.fit(eval_train_df[feature_cols], eval_train_df[target_cols])

    eval_predictions = eval_model.predict(eval_test_df[feature_cols])
    r2_per_target = {
        col: r2_score(eval_test_df[target_cols[i]], eval_predictions[:, i])
        for i, col in enumerate(target_cols)
    }

    print("\n80/20 held-out R^2 per imputed indicator:")
    for col, r2 in r2_per_target.items():
        print(f"  {col}: R^2 = {r2:.4f}")

    r2_df = pd.DataFrame(
        [{"indicator": col, "r2": r2} for col, r2 in r2_per_target.items()]
    )
    r2_df.to_csv(eval_path, index=False)
    print(f"Held-out R^2 per indicator saved to '{eval_path}'.\n")

    X_train = train_df[feature_cols]
    y_train = train_df[target_cols]

    print("Training production RandomForestRegressor model on all overlapping users...")
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
    OUTPUT_FILE = '../../data/prepare_data/final_combined_data.csv'
    EVAL_FILE = '../../data/prepare_data/random_forest_eval_r2.csv'

    merge_and_predict_missing_users(AIDEV_FILE, GITHUB_FILE, OUTPUT_FILE, EVAL_FILE)

import os
import mlflow
from mlflow.tracking import MlflowClient

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
mlflow.set_tracking_uri(TRACKING_URI)

experiment_name = "Token-Classification-NER"
mlflow.set_experiment(experiment_name)

print(f"Connecting to MLflow: {TRACKING_URI}")
print(f"Logging experiment: {experiment_name}")

with mlflow.start_run(run_name="bert-base-cased-conll2003") as run:
    run_id = run.info.run_id
    
    # 1. Log Parameters
    mlflow.log_params({
        "model_checkpoint": "bert-base-cased",
        "dataset": "conll2003",
        "task": "Token Classification (NER)",
        "epochs": 3,
        "batch_size": 8,
        "learning_rate": 2e-5,
        "weight_decay": 0.01,
        "optimizer": "AdamW"
    })
    
    # 2. Log Metrics (simulate epochs)
    epochs_data = [
        {"loss": 0.324, "f1": 0.865, "precision": 0.850, "recall": 0.881, "accuracy": 0.942},
        {"loss": 0.185, "f1": 0.902, "precision": 0.895, "recall": 0.910, "accuracy": 0.961},
        {"loss": 0.112, "f1": 0.923, "precision": 0.918, "recall": 0.928, "accuracy": 0.975},
    ]
    
    for epoch, metrics in enumerate(epochs_data, start=1):
        for metric_name, val in metrics.items():
            mlflow.log_metric(metric_name, val, step=epoch)
            
    print(f"Run {run_id} logged successfully with params and metrics.")

# 3. Register Model in Model Registry
client = MlflowClient(tracking_uri=TRACKING_URI)
model_name = "bert-base-ner"

try:
    client.create_registered_model(model_name, description="BERT Model for Named Entity Recognition fine-tuned on CoNLL-2003")
    print(f"Created registered model: {model_name}")
except Exception as e:
    print(f"Registered model note: {e}")

try:
    mv = client.create_model_version(
        name=model_name,
        source=f"runs:/{run_id}/artifacts",
        run_id=run_id,
        description="Initial production version of bert-base-ner"
    )
    print(f"Created model version: {mv.version}")
    
    client.transition_model_version_stage(
        name=model_name,
        version=mv.version,
        stage="Production"
    )
    print(f"Model version {mv.version} transitioned to Production!")
except Exception as e:
    print(f"Error creating model version: {e}")

print("MLflow population completed successfully!")

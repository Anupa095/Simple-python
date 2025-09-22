import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Expanded + Balanced Dataset (study hours, sleep hours, pass/fail)
X = np.array([
    [5, 7], [8, 6], [2, 5], [1, 4], [9, 8], [6, 6], [7, 5],
    [3, 6], [4, 4], [10, 7],
    # Extra Fail cases
    [0, 3], [1, 2], [2, 3], [3, 2], [1, 1],
    # Extra Pass cases
    [10, 9], [9, 7], [8, 8], [7, 9], [6, 8]
])
y = np.array([
    1, 1, 0, 0, 1, 1, 1, 0, 0, 1,   # original
    0, 0, 0, 0, 0,                  # new fail
    1, 1, 1, 1, 1                   # new pass
])

# 2. Normalize data
scaler = StandardScaler()
X = scaler.fit_transform(X)

# 3. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Build model (simpler + dropout)
model = Sequential([
    Dense(8, activation='relu', input_shape=(2,)),
    Dropout(0.2),
    Dense(4, activation='relu'),
    Dense(1, activation='sigmoid')
])

# 5. Compile model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# 6. Train model
history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=2,
    validation_data=(X_test, y_test),
    verbose=0
)

# 7. Evaluate
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"✅ Test Accuracy: {acc:.2f}")

# 8. Plot accuracy & loss
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Test Accuracy')
plt.legend()
plt.title("Accuracy Over Epochs")

plt.subplot(1,2,2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Test Loss')
plt.legend()
plt.title("Loss Over Epochs")

plt.show()

# 9. Manual input
study_hours = float(input("Enter study hours: "))
sleep_hours = float(input("Enter sleep hours: "))

new_student = np.array([[study_hours, sleep_hours]])
new_student = scaler.transform(new_student)
prediction = model.predict(new_student)

prob = prediction[0][0]
print("\n🔮 Pass Probability:", prob)
print("📊 Prediction:", "PASS ✅" if prob > 0.6 else "FAIL ❌")

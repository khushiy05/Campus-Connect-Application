<template>
  <section class="review-section">
    <div class="review-card">
      <div class="review-header">
        <h2 class="review-title">Share a Review</h2>
        <p class="review-subtitle">Tell us what you think about Campus Panel</p>
      </div>

      <form class="review-form" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            placeholder="Your name"
            required
          />
        </div>

        <div class="field">
          <label for="message">Message</label>
          <textarea
            id="message"
            v-model="form.message"
            rows="4"
            placeholder="Write your feedback here..."
            required
          ></textarea>
        </div>

        <div class="field">
          <label>Rating</label>
          <div class="stars">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="star-btn"
              :class="{ filled: star <= (hoverRating || form.rating) }"
              @click="form.rating = star"
              @mouseenter="hoverRating = star"
              @mouseleave="hoverRating = 0"
              :aria-label="`Rate ${star} star${star > 1 ? 's' : ''}`"
            >
              ★
            </button>
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="submitting">
          {{ submitting ? "Submitting..." : "Submit Review" }}
        </button>

        <p v-if="submitted" class="success-msg">
          Thanks for your review!
        </p>
      </form>
    </div>
  </section>
</template>

<script>
export default {
  name: "ReviewForm",
  data() {
    return {
      form: {
        name: "",
        message: "",
        rating: 0,
      },
      hoverRating: 0,
      submitting: false,
      submitted: false,
    };
  },
  methods: {
    async handleSubmit() {
      if (!this.form.rating) {
        alert("Please select a rating before submitting.");
        return;
      }
      this.submitting = true;
      try {
        const res = await fetch("/api/reviews", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.form),
        });
        const data = await res.json();

        if (!res.ok || !data.success) {
          throw new Error(data.error || "Failed to submit review.");
        }

        this.$emit("review-submitted", { ...this.form });

        this.submitted = true;
        this.form = { name: "", message: "", rating: 0 };
        setTimeout(() => (this.submitted = false), 3000);
      } catch (err) {
        alert(err.message || "Something went wrong. Please try again.");
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.review-section {
  padding: 32px 24px;
  display: flex;
  justify-content: center;
}

.review-card {
  width: 100%;
  max-width: 560px;
  background: #ffffff;
  border: 1px solid #e7e8f2;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 10px rgba(79, 70, 229, 0.06);
}

.review-header {
  margin-bottom: 24px;
}

.review-title {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f1147;
}

.review-subtitle {
  margin: 0;
  font-size: 14px;
  color: #7b7f9e;
}

.review-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 13px;
  font-weight: 600;
  color: #3d3466;
}

.field input,
.field textarea {
  border: 1px solid #dcdce8;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  color: #1f1147;
  background: #fafaff;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  resize: none;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  background: #ffffff;
}

.stars {
  display: flex;
  gap: 6px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 26px;
  line-height: 1;
  cursor: pointer;
  color: #dcdce8;
  padding: 0;
  transition: color 0.15s ease, transform 0.1s ease;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star-btn.filled {
  color: #f5a524;
}

.submit-btn {
  margin-top: 6px;
  background: #4f46e5;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #4338ca;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-msg {
  margin: 0;
  text-align: center;
  font-size: 13px;
  color: #16a34a;
  font-weight: 600;
}
</style>
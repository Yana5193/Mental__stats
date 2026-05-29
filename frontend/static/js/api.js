const BASE = "http://localhost:8000/api/v1";
const Q_BASE = "http://localhost:8001";

const Api = {
  async login(full_name, password) {
    const r = await fetch(`${BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, password }),
    });
    if (!r.ok) throw new Error("Неверное имя или пароль");
    return r.json();
  },

  async getQuestions(test_id = 1) {
    const r = await fetch(`${Q_BASE}/tests/${test_id}/questions`);
    if (!r.ok) throw new Error("Не удалось загрузить вопросы");
    return r.json();
  },

  async submitAnswers(emp_id, answers) {
    const r = await fetch(`${BASE}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ emp_id, answers }),
    });
    if (r.status === 429) throw new Error("Тест можно проходить раз в 30 дней");
    if (r.status === 422) {
      const body = await r.json();
      throw new Error(body.detail ?? "Ответы не прошли проверку");
    }
    if (!r.ok) throw new Error("Ошибка при сохранении результата");
    return r.json();
  },

  async getReminder(emp_id) {
    const r = await fetch(`${BASE}/reminder/${emp_id}`);
    if (!r.ok) throw new Error("Не удалось проверить напоминание");
    return r.json();
  },

  async getAnalytics() {
    const r = await fetch(`${BASE}/analytics`);
    if (!r.ok) throw new Error("Не удалось загрузить аналитику");
    return r.json();
  },
};
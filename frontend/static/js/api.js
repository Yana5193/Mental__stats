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

  async getDepartments() {
    const r = await fetch(`${BASE}/departments`);
    if (!r.ok) throw new Error("Не удалось загрузить отделы");
    return r.json();
  },

  async addEmployee(data) {
    const r = await fetch(`${BASE}/employees`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!r.ok) throw new Error("Не удалось добавить сотрудника");
    return r.json();
  },

  async getTests() {
    const r = await fetch(`${Q_BASE}/tests`);
    if (!r.ok) throw new Error("Не удалось загрузить тесты");
    return r.json();
  },

  async addTest(name) {
    const r = await fetch(`${Q_BASE}/tests`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (!r.ok) throw new Error("Не удалось создать тест");
    return r.json();
  },

  async addQuestion(test_id, question) {
    const r = await fetch(`${Q_BASE}/questions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ test_id, question }),
    });
    if (!r.ok) throw new Error("Не удалось добавить вопрос");
    return r.json();
  },
};

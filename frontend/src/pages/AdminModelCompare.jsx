import { useState } from "react";
import { api } from "../api";
import { Empty, ErrorState, Loading } from "../components/StateViews";

const SAMPLES = [
  "Phim dài lê thê, nửa đầu buồn ngủ thật sự.",
  "Diễn xuất tự nhiên, cảnh cuối làm mình xúc động.",
  "Ko hay như quảng cáo, hơi thất vọng.",
  "Hình ảnh đẹp nhưng kịch bản nhảm và thiếu logic.",
  "Bình thường, xem giải trí cuối tuần cũng ổn.",
];

const LABELS = { tieu_cuc: "Tiêu cực", binh_thuong: "Bình thường" };
const MODEL_NAMES = {
  phobert: "PhoBERT A", phobert_b: "PhoBERT B", svm: "SVM",
  lr: "Logistic Regression", nb: "Naive Bayes",
};

export default function AdminModelCompare() {
  const [text, setText] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const predict = async (event) => {
    event?.preventDefault();
    const value = text.trim();
    if (!value) {
      setError("Hãy nhập nội dung cần chấm điểm.");
      setResults(null);
      return;
    }
    setLoading(true);
    setError("");
    try {
      setResults(await api.admin.predict(value));
    } catch (err) {
      setResults(null);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const useSample = (sample) => {
    setText(sample);
    setError("");
    setResults(null);
  };

  return (
    <div className="container admin-model-compare">
      <h1 className="page-title">So sánh mô hình</h1>
      <p className="muted admin__intro">
        Nhập cùng một câu để xem nhãn, điểm tiêu cực và thời gian suy luận của từng mô hình.
        PhoBERT B là model mặc định; PhoBERT A được giữ để đối chiếu và fallback.
        Điểm SVM là sigmoid của decision function, không phải xác suất đã hiệu chỉnh.
      </p>

      <form className="model-compare-form" onSubmit={predict}>
        <label className="field" htmlFor="compare-text">
          <span>Nội dung bình luận</span>
          <textarea id="compare-text" rows="4" maxLength="1000" value={text}
            onChange={(event) => { setText(event.target.value); setError(""); }}
            placeholder="Ví dụ: Phim dài lê thê..." />
        </label>
        <div className="model-samples" aria-label="Câu mẫu">
          {SAMPLES.map((sample) => (
            <button type="button" className="model-sample" key={sample} onClick={() => useSample(sample)}>
              {sample}
            </button>
          ))}
        </div>
        <button className="btn btn--primary" type="submit" disabled={loading}>
          {loading ? "Đang chấm điểm..." : "Chấm điểm"}
        </button>
      </form>

      <section className="model-results" aria-live="polite" aria-busy={loading}>
        <h2 className="section-title">Kết quả</h2>
        {loading ? <Loading label="Các mô hình đang chấm điểm..." />
          : error ? <ErrorState message={error} onRetry={text.trim() ? predict : undefined} />
            : results === null ? <Empty><p>Nhập một câu hoặc chọn câu mẫu để bắt đầu so sánh.</p></Empty>
              : results.length === 0 ? <Empty><p>Không có mô hình nào sẵn sàng.</p></Empty>
                : <div className="table-wrap"><table className="admin-table model-results-table">
                  <thead><tr><th>Mô hình</th><th>Phiên bản</th><th>Nhãn</th><th>Điểm</th><th>Thời gian</th></tr></thead>
                  <tbody>{results.map((result) => (
                    <tr key={`${result.model}-${result.version}`}>
                      <td><strong>{MODEL_NAMES[result.model] ?? result.model}</strong></td>
                      <td>{result.version}</td>
                      <td><span className={`label ${result.label === "tieu_cuc" ? "label--neg" : "label--ok"}`}>
                        {LABELS[result.label] ?? result.label}
                      </span></td>
                      <td>{Number(result.score).toFixed(4)}</td>
                      <td>{Number(result.ms).toFixed(3)} ms</td>
                    </tr>
                  ))}</tbody>
                </table></div>}
      </section>
    </div>
  );
}

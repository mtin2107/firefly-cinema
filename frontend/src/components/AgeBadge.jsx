const NOTE = { P: "Mọi lứa tuổi", T13: "Từ 13 tuổi", T16: "Từ 16 tuổi", T18: "Từ 18 tuổi" };
export default function AgeBadge({ rating }) {
  return <span className={`age age--${rating}`} title={NOTE[rating]}>{rating}</span>;
}

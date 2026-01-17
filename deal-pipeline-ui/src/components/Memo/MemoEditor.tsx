const SECTIONS = [
  "Summary",
  "Market",
  "Product",
  "Traction",
  "Risks",
  "Open Questions",
];

export default function MemoEditor({ memo, onSave }: any) {
  const [data, setData] = useState(memo);

  return (
    <>
      {SECTIONS.map(sec => (
        <textarea
          key={sec}
          value={data[sec] || ""}
          onChange={e =>
            setData({ ...data, [sec]: e.target.value })
          }
        />
      ))}
      <button onClick={() => onSave(data)}>Save (New Version)</button>
    </>
  );
}

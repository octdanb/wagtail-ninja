import React from "react";

interface RenderJSONProps {
  data: any;
}

const RenderJSON: React.FC<RenderJSONProps> = ({ data }) => {
  if (
    typeof data === "string" ||
    typeof data === "number" ||
    typeof data === "boolean"
  ) {
    return <span>{String(data)}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <ul>
        {data.map((item, index) => (
          <li key={index}>
            <RenderJSON data={item} />
          </li>
        ))}
      </ul>
    );
  }

  if (typeof data === "object" && data !== null) {
    return (
      <div style={{ paddingLeft: "1em", borderLeft: "2px solid #ccc" }}>
        {Object.entries(data).map(([key, value]) => (
          <div key={key}>
            <strong>{key}:</strong> <RenderJSON data={value} />
          </div>
        ))}
      </div>
    );
  }

  return <span>null</span>;
};

export default RenderJSON;

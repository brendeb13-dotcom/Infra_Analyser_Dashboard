import { useState } from "react";

export default function useGlobalSearch() {
  const [query, setQuery] = useState("");

  const filter = (items, keys) => {
    if (!query) return items;

    return items.filter(item =>
      keys.some(key => {
        const value = key.split(".").reduce((o, k) => o?.[k], item);
        return String(value || "")
          .toLowerCase()
          .includes(query.toLowerCase());
      })
    );
  };

  return { query, setQuery, filter };
}

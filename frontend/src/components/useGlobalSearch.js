import { useState } from "react";

/**
 * Generic global search hook
 * Works with arrays of objects
 */
export default function useGlobalSearch() {
  const [query, setQuery] = useState("");

  const filter = (data = [], fields = []) => {
    if (!query) return data;

    const q = query.toLowerCase();

    return data.filter((item) =>
      fields.some((field) => {
        const value = item[field];
        if (value === undefined || value === null) return false;
        return String(value).toLowerCase().includes(q);
      })
    );
  };

  return {
    query,
    setQuery,
    filter
  };
}

import { useEffect, useState } from "react";

  export function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    // Якщо значення змінилося раніше, старий таймер скасовуємо
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
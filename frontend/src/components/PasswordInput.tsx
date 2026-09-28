import { useState } from "react";

interface PasswordInputProps {
  id?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  minLength?: number;
}

// Campo de contrasena con boton para mostrarla u ocultarla mientras se escribe.
export function PasswordInput({ id, placeholder, value, onChange, minLength }: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="password-field">
      <input
        id={id}
        placeholder={placeholder}
        type={visible ? "text" : "password"}
        required
        minLength={minLength}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <button
        type="button"
        className="password-toggle"
        aria-pressed={visible}
        onClick={() => setVisible((current) => !current)}
      >
        {visible ? "Ocultar" : "Ver"}
      </button>
    </div>
  );
}

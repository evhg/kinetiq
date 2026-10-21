"use client";

import { models, type ModelId } from "@/content/site";

/** Segmented choice between the two rackets. A radio group, so arrows work. */
export function ModelPicker({ value, onChange, name = "model" }: { value: ModelId; onChange: (m: ModelId) => void; name?: string }) {
  return (
    <fieldset className="picker">
      <legend className="visually-hidden">Choose your racket</legend>
      {(Object.keys(models) as ModelId[]).map((id) => (
        <label key={id} className="picker-option" data-checked={value === id}>
          <input type="radio" name={name} value={id} checked={value === id} onChange={() => onChange(id)} />
          <span>{models[id].name}</span>
        </label>
      ))}
    </fieldset>
  );
}

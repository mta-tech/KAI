'use client';

import { useState, useCallback, useId } from 'react';

export type ValidationRule<T = any> = (
  value: T,
  formData?: Record<string, any>
) => string | undefined;

export interface FieldValidationRules<T = any> {
  required?: string | boolean;
  minLength?: { value: number; message: string };
  maxLength?: { value: number; message: string };
  pattern?: { value: RegExp; message: string };
  min?: { value: number; message: string };
  max?: { value: number; message: string };
  custom?: ValidationRule<T>;
  validate?: ValidationRule<T>;
}

export interface FieldValidationResult {
  isValid: boolean;
  error?: string;
}

export interface UseFormValidationOptions<T extends Record<string, any>> {
  initialValues: T;
  validationRules: Partial<Record<keyof T, FieldValidationRules>>;
  onSubmit?: (values: T) => void | Promise<void>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

export interface FieldMeta {
  touched: boolean;
  dirty: boolean;
  error?: string;
  isValid: boolean;
}

export function useFormValidation<T extends Record<string, any>>({
  initialValues,
  validationRules,
  onSubmit,
  validateOnChange = true,
  validateOnBlur = true,
}: UseFormValidationOptions<T>) {
  const [values, setValues] = useState<T>(initialValues);
  const [fieldsMeta, setFieldsMeta] = useState<Partial<Record<keyof T, FieldMeta>>>(
    () => {
      const meta: Partial<Record<keyof T, FieldMeta>> = {};
      (Object.keys(initialValues) as Array<keyof T>).forEach(key => {
        meta[key] = {
          touched: false,
          dirty: false,
          isValid: true,
        };
      });
      return meta;
    }
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const formId = useId();

  const validateField = useCallback(
    (fieldName: keyof T, value: any, allValues?: T): FieldValidationResult => {
      const rules = validationRules[fieldName];
      if (!rules) {
        return { isValid: true };
      }

      // Required validation
      if (rules.required) {
        const isRequired = typeof rules.required === 'string' || rules.required === true;
        if (isRequired && (!value || (typeof value === 'string' && !value.trim()))) {
          return {
            isValid: false,
            error: typeof rules.required === 'string' ? rules.required : 'This field is required',
          };
        }
      }

      // Skip other validations if field is empty and not required
      if (!value || (typeof value === 'string' && !value.trim())) {
        return { isValid: true };
      }

      // Min length validation
      if (rules.minLength && typeof value === 'string') {
        if (value.length < rules.minLength.value) {
          return {
            isValid: false,
            error: rules.minLength.message,
          };
        }
      }

      // Max length validation
      if (rules.maxLength && typeof value === 'string') {
        if (value.length > rules.maxLength.value) {
          return {
            isValid: false,
            error: rules.maxLength.message,
          };
        }
      }

      // Pattern validation
      if (rules.pattern && typeof value === 'string') {
        if (!rules.pattern.value.test(value)) {
          return {
            isValid: false,
            error: rules.pattern.message,
          };
        }
      }

      // Min validation for numbers
      if (rules.min && typeof value === 'number') {
        if (value < rules.min.value) {
          return {
            isValid: false,
            error: rules.min.message,
          };
        }
      }

      // Max validation for numbers
      if (rules.max && typeof value === 'number') {
        if (value > rules.max.value) {
          return {
            isValid: false,
            error: rules.max.message,
          };
        }
      }

      // Custom validation
      if (rules.custom) {
        const error = rules.custom(value, allValues || values);
        if (error) {
          return { isValid: false, error };
        }
      }

      // Validate function
      if (rules.validate) {
        const error = rules.validate(value, allValues || values);
        if (error) {
          return { isValid: false, error };
        }
      }

      return { isValid: true };
    },
    [validationRules, values]
  );

  const validateAllFields = useCallback((): boolean => {
    const newMeta: Partial<Record<keyof T, FieldMeta>> = {};
    let allValid = true;

    (Object.keys(validationRules) as Array<keyof T>).forEach(fieldName => {
      const result = validateField(fieldName, values[fieldName], values);
      newMeta[fieldName] = {
        touched: true,
        dirty: fieldsMeta[fieldName]?.dirty || false,
        isValid: result.isValid,
        error: result.error,
      };
      if (!result.isValid) {
        allValid = false;
      }
    });

    setFieldsMeta(prev => ({ ...prev, ...newMeta }));
    return allValid;
  }, [validateField, values, validationRules, fieldsMeta]);

  const isFormValid = useCallback(() => {
    return (Object.keys(fieldsMeta) as Array<keyof T>).every(
      fieldName => fieldsMeta[fieldName]?.isValid !== false
    );
  }, [fieldsMeta]);

  const handleChange = useCallback(
    (fieldName: keyof T, value: any) => {
      setValues(prev => ({ ...prev, [fieldName]: value }));
      setFieldsMeta(prev => ({
        ...prev,
        [fieldName]: {
          ...prev[fieldName],
          dirty: true,
        },
      }));

      if (validateOnChange || fieldsMeta[fieldName]?.touched) {
        const result = validateField(fieldName, value, { ...values, [fieldName]: value });
        setFieldsMeta(prev => ({
          ...prev,
          [fieldName]: {
            touched: true,
            dirty: true,
            isValid: result.isValid,
            error: result.error,
          },
        }));
      }
    },
    [validateOnChange, validateField, values, fieldsMeta]
  );

  const handleBlur = useCallback(
    (fieldName: keyof T) => {
      if (validateOnBlur) {
        const result = validateField(fieldName, values[fieldName], values);
        setFieldsMeta(prev => ({
          ...prev,
          [fieldName]: {
            ...prev[fieldName],
            touched: true,
            isValid: result.isValid,
            error: result.error,
          },
        }));
      }
    },
    [validateOnBlur, validateField, values]
  );

  const handleSubmit = useCallback(
    async (event?: React.FormEvent) => {
      if (event) {
        event.preventDefault();
      }

      setIsSubmitted(true);
      const isValid = validateAllFields();

      if (isValid && onSubmit) {
        setIsSubmitting(true);
        try {
          await onSubmit(values);
        } finally {
          setIsSubmitting(false);
        }
      }
    },
    [onSubmit, validateAllFields, values]
  );

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setIsSubmitted(false);
    setIsSubmitting(false);
    setFieldsMeta(() => {
      const meta: Partial<Record<keyof T, FieldMeta>> = {};
      (Object.keys(initialValues) as Array<keyof T>).forEach(key => {
        meta[key] = {
          touched: false,
          dirty: false,
          isValid: true,
        };
      });
      return meta;
    });
  }, [initialValues]);

  const getFieldProps = useCallback(
    (fieldName: keyof T) => {
      const meta = fieldsMeta[fieldName];
      const showError = meta?.touched && meta.error;
      const fieldId = `${formId}-${String(fieldName)}`;
      const errorId = `${fieldId}-error`;

      return {
        id: fieldId,
        name: String(fieldName),
        value: values[fieldName],
        onChange: (value: any) => handleChange(fieldName, value),
        onBlur: () => handleBlur(fieldName),
        error: showError ? meta.error : undefined,
        errorId,
        'aria-invalid': showError ? true : undefined,
        'aria-describedby': showError ? errorId : undefined,
        isDirty: meta?.dirty || false,
        isTouched: meta?.touched || false,
        isValid: meta?.isValid !== false,
      };
    },
    [fieldsMeta, values, handleChange, handleBlur, formId]
  );

  return {
    values,
    fieldsMeta,
    isSubmitting,
    isSubmitted,
    isFormValid: isFormValid(),
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    getFieldProps,
    setValues,
    formId,
  };
}

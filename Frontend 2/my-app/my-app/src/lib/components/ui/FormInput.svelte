<script>
	let {
		id,
		label = '',
		tipo = 'text',
		valor = $bindable(''),
		placeholder = '',
		requerido = false,
		deshabilitado = false,
		mensajeAyuda = '',
		error = ''
	} = $props();
</script>

<div class="form-field">
	{#if label}
		<label for={id} class="form-label">
			{label}

			{#if requerido}
				<span class="required-mark" aria-label="Campo obligatorio">*</span>
			{/if}
		</label>
	{/if}

	<input
		{id}
		type={tipo}
		bind:value={valor}
		{placeholder}
		required={requerido}
		disabled={deshabilitado}
		aria-invalid={error ? 'true' : undefined}
		aria-describedby={error ? `${id}-error` : mensajeAyuda ? `${id}-help` : undefined}
		class:error-input={!!error}
		class="form-control-custom"
	/>

	{#if error}
		<small id={`${id}-error`} class="form-error">
			{error}
		</small>
	{:else if mensajeAyuda}
		<small id={`${id}-help`} class="form-help">
			{mensajeAyuda}
		</small>
	{/if}
</div>

<style>
	.form-field {
		display: flex;
		flex-direction: column;
		gap: 8px;
		width: 100%;
		min-width: 0;
	}

	.form-label {
		color: #dbe5f5;
		font-size: 13px;
		font-weight: 600;
	}

	.required-mark {
		margin-left: 3px;
		color: #f87171;
	}

	.form-control-custom {
		width: 100%;
		min-height: 44px;
		padding: 11px 13px;
		border: 1px solid #3b4b63;
		border-radius: 9px;
		outline: none;
		background: #172338;
		color: #f8fafc;
		font-family: inherit;
		font-size: 14px;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.form-control-custom::placeholder {
		color: #8293ac;
	}

	.form-control-custom:focus {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 15%);
	}

	.form-control-custom:disabled {
		background: #1e293b;
		color: #94a3b8;
		cursor: not-allowed;
		opacity: 0.7;
	}

	.form-control-custom.error-input {
		border-color: #f87171;
	}

	.form-control-custom.error-input:focus {
		box-shadow: 0 0 0 3px rgb(248 113 113 / 12%);
	}

	.form-help,
	.form-error {
		font-size: 12px;
		line-height: 1.5;
	}

	.form-help {
		color: #94a3b8;
	}

	.form-error {
		color: #fca5a5;
	}
</style>

<script>
	let {
		id,
		label = '',
		valor = $bindable(''),
		opciones = [],
		placeholder = 'Selecciona una opción',
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

	<select
		{id}
		bind:value={valor}
		required={requerido}
		disabled={deshabilitado}
		aria-invalid={error ? 'true' : undefined}
		aria-describedby={error ? `${id}-error` : mensajeAyuda ? `${id}-help` : undefined}
		class:error-input={!!error}
		class="form-select-custom"
	>
		<option value="" disabled>
			{placeholder}
		</option>

		{#each opciones as opcion (opcion.valor)}
			<option value={opcion.valor}>
				{opcion.etiqueta}
			</option>
		{/each}
	</select>

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

	.form-select-custom {
		width: 100%;
		min-height: 44px;
		padding: 11px 36px 11px 13px;
		border: 1px solid #3b4b63;
		border-radius: 9px;
		outline: none;
		background-color: #172338;
		color: #f8fafc;
		font-family: inherit;
		font-size: 14px;
		cursor: pointer;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.form-select-custom:focus {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 15%);
	}

	.form-select-custom:disabled {
		background-color: #1e293b;
		color: #94a3b8;
		cursor: not-allowed;
		opacity: 0.7;
	}

	.form-select-custom option {
		background: #172338;
		color: #f8fafc;
	}

	.form-select-custom.error-input {
		border-color: #f87171;
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

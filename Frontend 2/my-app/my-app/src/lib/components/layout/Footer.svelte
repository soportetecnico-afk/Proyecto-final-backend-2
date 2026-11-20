<footer class="footer">
	<div class="footer-contenido">
		<div class="footer-identidad">
			<span class="footer-logo">CUL</span>

			<div>
				<strong>Sistema de Reservas</strong>
				<p>Gestión de Espacios Universitarios</p>
			</div>
		</div>

		<div class="footer-derechos">
			<span>Plataforma de gestión universitaria</span>
			<span>© {new Date().getFullYear()} CUL</span>
		</div>
	</div>
</footer>

<style>
	.footer {
		width: 100%;
		margin-top: auto;
		padding: 22px 28px;
		background: #111c31;
		border-top: 1px solid #29364d;
		color: #cbd5e1;
	}

	.footer-contenido {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		max-width: 1600px;
		margin: 0 auto;
	}

	.footer-identidad {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.footer-logo {
		display: grid;
		place-items: center;
		width: 38px;
		height: 38px;
		flex-shrink: 0;
		border: 1px solid #475569;
		border-radius: 9px;
		color: #93c5fd;
		font-size: 14px;
		font-weight: 800;
	}

	.footer-identidad strong {
		color: #f8fafc;
		font-size: 13px;
	}

	.footer-identidad p {
		margin: 4px 0 0;
		color: #94a3b8;
		font-size: 12px;
	}

	.footer-derechos {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 5px;
		color: #94a3b8;
		font-size: 12px;
		text-align: right;
	}

	@media (max-width: 600px) {
		.footer {
			padding: 20px 16px;
		}

		.footer-contenido {
			align-items: flex-start;
			flex-direction: column;
		}

		.footer-derechos {
			align-items: flex-start;
			text-align: left;
		}
	}
</style>

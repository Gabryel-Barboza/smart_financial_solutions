const UploadPanel = ({ handleUpload, setSelectedNav }) => (
  <div className="p-8 bg-white shadow-xl rounded-2xl h-full flex flex-col items-center justify-center text-center">
    <h2 className="text-2xl font-extrabold text-gray-800 mb-4">Novo Lote Fiscal</h2>
    <p className="text-gray-600 mb-6 max-w-sm">
      Envie seu arquivo (.csv, .xlsx ou .zip) para iniciar o fluxo de agentes (FastAPI + LangGraph).
    </p>
    <div
      className="w-full max-w-xs p-6 border-2 border-dashed border-blue-400 rounded-xl bg-blue-50 hover:bg-blue-100 cursor-pointer transition-colors duration-200"
      onClick={() => document.getElementById('file-upload').click()}
    >
      <svg
        className="w-8 h-8 mx-auto text-blue-500 mb-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v8"
        ></path>
      </svg>
      <p className="text-sm text-blue-700 font-medium">
        Clique para selecionar ou arraste o arquivo
      </p>
      <input
        type="file"
        id="file-upload"
        className="hidden"
        onChange={(e) => {
          if (e.target.files.length) {
            handleUpload(e.target.files[0].name);
            e.target.value = null; // Reset input
          }
        }}
      />
    </div>
    <button
      onClick={() => setSelectedNav('Dashboard')}
      className="mt-6 text-sm font-medium text-blue-600 hover:text-blue-800 transition duration-150"
    >
      Ver Status do Workflow
    </button>
  </div>
);

export default UploadPanel;

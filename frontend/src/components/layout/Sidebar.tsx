import { navItems } from '../../data/navData';
import SVGIcon from '../Shared/SVGIcon'; // Componente auxiliar

const Sidebar = ({ selectedNav, setSelectedNav }) => (
  <div className="hidden lg:flex flex-col w-64 bg-gray-900 text-white p-6 shadow-2xl">
    <div className="flex items-center space-x-3 mb-10 pt-2">
      <svg
        className="w-8 h-8 text-blue-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M9 19V6l12-3v14M9 19c-1.33 0-2.5-.56-3.33-1.4L2 14v4c0 2.21 1.79 4 4 4h12c1.33 0 2.5-.56 3.33-1.4L22 18V6l-3 1.5"
        ></path>
      </svg>
      <span className="text-xl font-bold tracking-wider">Agent Fiscal</span>
    </div>
    <nav className="flex-1">
      {navItems.map((item) => (
        <a
          key={item.name}
          href="#"
          onClick={() => setSelectedNav(item.name)}
          className={`
                        flex items-center px-4 py-3 rounded-xl mb-2 transition-all duration-200
                        ${
                          selectedNav === item.name
                            ? 'bg-blue-600 text-white font-semibold shadow-lg'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        }
                    `}
        >
          <SVGIcon path={item.icon} className="w-5 h-5 mr-3" />
          {item.name}
        </a>
      ))}
    </nav>
    <div className="pt-6 border-t border-gray-700">
      <p className="text-sm text-gray-500">FastAPI & LangGraph Powered</p>
    </div>
  </div>
);

export default Sidebar;

import { navItems } from '../../data/navData';
import { FaFileZipper } from 'react-icons/fa6';
import type { CurrentNavSchema } from '../../schemas/PropsSchema';

const Sidebar = ({ selectedNav, setSelectedNav }: CurrentNavSchema) => {
  return (
    <div className="hidden lg:flex flex-col w-64 bg-gray-900 text-white p-6 shadow-2xl">
      <div className="flex items-center space-x-3 mb-10 pt-2">
        <FaFileZipper />
        <span className="text-xl font-bold tracking-wider">Agente Fiscal</span>
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
                            ? 'bg-blue-600 text-black font-bold shadow-lg'
                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        }
                    `}
          >
            <span className="mr-2">{item.icon}</span>
            <span>{item.name}</span>
          </a>
        ))}
      </nav>

      <div className="pt-6 border-t border-gray-700">
        <p className="text-sm text-gray-500">Powered by LangChain</p>
        <p className="text-sm text-gray-500">
          Favicon by{' '}
          <a
            className="text-blue-600 hover:bg-blue-600 hover:text-black"
            href="https://icons8.com"
            rel="external"
          >
            Icons8
          </a>
        </p>
      </div>
    </div>
  );
};

export default Sidebar;

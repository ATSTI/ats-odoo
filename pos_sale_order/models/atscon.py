# -*- encoding: iso-8859-1 -*-

#import fdb
import fdb as Database
#import configparser
import base64


class Conexao:

    def __init__(self, host, database):
        #import pudb;pu.db
        self.connection = Database.connect(dsn=host+':' + database, \
            user='sysdba', password='masterkey')
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return ''
            #except:
            ##import pudb;pu.db
            #        except Database.IntegrityError, e:
            #raise utils.IntegrityError, utils.IntegrityError(*tuple(e)+('sql: '+query,)+args), sys.exc_info()[2]
        except Database.DatabaseError as e:
            self.connection.rollback()
            """
            if 'IDX_CODPRO' in e:
                x = e.find('=')
                if (x > 0):
                    x = 'Ja existe este Cod Produto : %s' %(
                        e[e.find('=')+3:e.find('=')+16]
                    )
                    return x
            if 'IDX_CODBARRA' in e:
                x = e.find('=')
                if (x > 0):
                    x = 'Ja existe este Cod Barra : %s' %(
                        e[e.find('=')+3:e.find('=')+16]
                    )
                    return x
            """
            return str(e)
            #x = tuple(e)
            #print ('Erro :%s' %(query))
            
        except Database.DatabaseError as e:
            self.connection.rollback()
            return e
            

    def query(self, query):
        #cursor = self.connection.cursor( MySQLdb.cursors.DictCursor )
        cur = self.cursor.execute(query)
        return cur.fetchall()

    #def sistema(self):
    #    return self.odoo     


    def __del__(self):
        self.connection.close()
